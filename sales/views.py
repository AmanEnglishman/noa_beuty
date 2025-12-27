from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import Sale, SaleItem, PaymentMethod, PrintQueue
from products.models import Perfume, BottleType, CosmeticProduct
from inventory.services import apply_sale_item_to_stocks

from django.http import FileResponse, Http404, JsonResponse
import os

import requests

@csrf_exempt
def enqueue_print(request, sale_id):
    PrintQueue.objects.create(
        sale_id=sale_id,
        printed=False
    )
    return JsonResponse({"status": "queued"})


# =========================
# Продажи за сегодня
# =========================
def sales_today(request):
    today = timezone.localdate()

    sales = (
        Sale.objects
        .filter(sale_date__date=today)
        .select_related("payment_method")
        .prefetch_related("items")
        .order_by("-sale_date")
    )

    return render(
        request,
        "sales/sales_today.html",
        {
            "sales": sales,
            "today": today,
        }
    )



# =========================
# Создание продажи 
# =========================
def sale_create(request):
    perfumes = Perfume.objects.select_related("brand").all()
    bottles = BottleType.objects.all()
    cosmetics = CosmeticProduct.objects.all()
    payment_methods = PaymentMethod.objects.filter(is_active=True)

    error = None

    if request.method == "POST":
        try:
            with transaction.atomic():

                # ===== ТИП ОПЛАТЫ =====
                payment_method_id = request.POST.get("payment_method")
                if not payment_method_id:
                    raise ValueError("Не выбран тип оплаты")

                payment_method = get_object_or_404(
                    PaymentMethod, id=payment_method_id
                )

                items_data = []
                items_total = 0

                types = request.POST.getlist("item_type")
                perfumes_ids = request.POST.getlist("perfume")
                cosmetics_ids = request.POST.getlist("cosmetic")
                ml_qties = request.POST.getlist("ml_qty")
                bottle_qties = request.POST.getlist("bottle_qty")
                bottle_type_ids = request.POST.getlist("bottle_type")
                atomizer_qties = request.POST.getlist("atomizer_qty")
                prices = request.POST.getlist("price")
                item_discounts = request.POST.getlist("item_discount")

                # ===== СБОР ПОЗИЦИЙ =====
                for i, sale_type in enumerate(types):

                    perfume_id = perfumes_ids[i] or None
                    cosmetic_id = cosmetics_ids[i] or None

                    ml = float(ml_qties[i]) if ml_qties[i] else 0
                    bottles_count = int(bottle_qties[i]) if bottle_qties[i] else 0
                    bottle_type_id = bottle_type_ids[i] or None
                    atomizer_count = int(atomizer_qties[i]) if atomizer_qties[i] else 0

                    price = int(prices[i]) if prices[i] else 0
                    discount_percent = int(item_discounts[i]) if item_discounts[i] else 0

                    # ---- QTY ----
                    if sale_type == "split":
                        qty = ml
                    elif sale_type in ("full", "cosmetic"):
                        qty = bottles_count
                    else:
                        qty = 1

                    base_total = price * qty
                    discount_sum = round(base_total * discount_percent / 100)
                    line_total = max(0, base_total - discount_sum)

                    items_total += line_total

                    # ---- ПЛАТНАЯ ТАРА ----
                    if sale_type == "split" and bottle_type_id and atomizer_count > 0:
                        bottle_type = BottleType.objects.filter(id=bottle_type_id).first()
                        if bottle_type and bottle_type.is_paid:
                            items_total += bottle_type.price * atomizer_count

                    items_data.append({
                        "sale_type": sale_type,
                        "perfume_id": perfume_id,
                        "cosmetic_id": cosmetic_id,
                        "ml": ml,
                        "bottles_count": bottles_count,
                        "bottle_type_id": bottle_type_id,
                        "bottle_count": atomizer_count if sale_type == "split" else bottles_count,
                        "unit_price": price,
                        "discount_percent": discount_percent,
                        "line_total": line_total,
                    })

                # ===== СОЗДАНИЕ ЧЕКА =====
                sale_discount_percent = int(request.POST.get("sale_discount", 0))

                sale = Sale.objects.create(
                    payment_method=payment_method,
                    discount_percent=sale_discount_percent,
                    total=0,
                )

                # ===== СОЗДАНИЕ ПОЗИЦИЙ =====
                for item in items_data:
                    sale_item = SaleItem.objects.create(
                        sale=sale,
                        sale_type=item["sale_type"],
                        perfume_id=item["perfume_id"],
                        cosmetic_id=item["cosmetic_id"],
                        ml=item["ml"],
                        bottles_count=item["bottles_count"],
                        bottle_count=item["bottle_count"],
                        bottle_type_id=item["bottle_type_id"],
                        unit_price=item["unit_price"],
                        discount_percent=item["discount_percent"],
                        line_total=item["line_total"],
                    )

                    apply_sale_item_to_stocks(
                        sale_type=sale_item.sale_type,
                        perfume=sale_item.perfume,
                        cosmetic=sale_item.cosmetic,
                        bottle_type=sale_item.bottle_type,
                        bottles_count=sale_item.bottles_count,
                        ml=sale_item.ml,
                        bottle_count=sale_item.bottle_count,
                    )

                # ===== СКИДКА НА ЧЕК =====
                sale_discount_sum = round(
                    items_total * sale.discount_percent / 100
                )

                sale.total = max(0, items_total - sale_discount_sum)
                sale.save()

                # ===== В ОЧЕРЕДЬ ПЕЧАТИ =====
                PrintQueue.objects.create(sale=sale)

                messages.success(request, "Продажа успешно сохранена")
                return redirect("sales_today")

        except Exception as e:
            error = f"Ошибка при сохранении продажи: {e}"

    return render(
        request,
        "sales/sale_create.html",
        {
            "perfumes": perfumes,
            "bottles": bottles,
            "cosmetics": cosmetics,
            "payment_methods": payment_methods,
            "error": error,
        }
    )






# =================================================
# PRINT AGENT: взять следующий чек из очереди
# =================================================
@csrf_exempt
def get_next_print(request):
    item = (
        PrintQueue.objects
        .filter(printed=False)
        .order_by("created_at")
        .first()
    )

    if not item:
        return JsonResponse({"sale_id": None})

    return JsonResponse({"sale_id": item.sale_id})


# =================================================
# PRINT AGENT: отметить чек как напечатанный
# =================================================
@csrf_exempt
def mark_printed(request, sale_id):
    PrintQueue.objects.filter(
        sale_id=sale_id,
        printed=False
    ).update(printed=True)

    return JsonResponse({"status": "ok"})

from django.http import HttpResponse
from .services.receipt_printer import render_sale_receipt_png

def receipt_png(request, sale_id):
    png = render_sale_receipt_png(sale_id)
    return HttpResponse(png, content_type="image/png")
