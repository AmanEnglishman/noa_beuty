from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib import messages

from .models import Sale, SaleItem
from products.models import Perfume, BottleType, CosmeticProduct
from inventory.services import apply_sale_item_to_stocks
from .services.receipt_printer import print_sale_receipt


# =========================
# Продажи за сегодня
# =========================
def sales_today(request):
    today = timezone.localdate()

    sales = (
        Sale.objects
        .filter(sale_date__date=today)
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
    error = None

    if request.method == "POST":
        try:
            with transaction.atomic():
                items_data = []
                total = 0

                types = request.POST.getlist("item_type")
                perfumes_ids = request.POST.getlist("perfume")
                cosmetics_ids = request.POST.getlist("cosmetic")
                ml_qties = request.POST.getlist("ml_qty")
                bottle_qties = request.POST.getlist("bottle_qty")
                bottle_type_ids = request.POST.getlist("bottle_type")
                atomizer_qties = request.POST.getlist("atomizer_qty")
                prices = request.POST.getlist("price")
                item_discounts = request.POST.getlist("item_discount")

                # -------- Сбор позиций --------
                for i, sale_type in enumerate(types):
                    perfume_id = perfumes_ids[i] or None
                    cosmetic_id = cosmetics_ids[i] or None

                    ml = float(ml_qties[i]) if ml_qties[i] else 0
                    bottles_count = int(bottle_qties[i]) if bottle_qties[i] else 0
                    bottle_type_id = bottle_type_ids[i] or None
                    atomizer_count = int(atomizer_qties[i]) if atomizer_qties[i] and sale_type == "split" else 0

                    price = int(prices[i]) if prices[i] else 0
                    discount = int(item_discounts[i]) if item_discounts[i] else 0

                    if sale_type == "split":
                        qty = ml
                    elif sale_type in ("full", "cosmetic"):
                        qty = bottles_count
                    else:
                        qty = 1

                    line_total = max(0, price * qty - discount)
                    total += line_total
                    
                    # Добавляем стоимость платной тары к итогу для распива
                    if sale_type == "split" and bottle_type_id and atomizer_count > 0:
                        try:
                            bottle_type = BottleType.objects.get(id=bottle_type_id)
                            if bottle_type.is_paid:
                                total += bottle_type.price * atomizer_count
                        except BottleType.DoesNotExist:
                            pass

                    items_data.append({
                        "sale_type": sale_type,
                        "perfume_id": perfume_id,
                        "cosmetic_id": cosmetic_id,
                        "ml": ml,
                        "bottles_count": bottles_count,
                        "bottle_type_id": bottle_type_id,
                        "atomizer_count": atomizer_count,
                        "unit_price": price,
                        "discount": discount,
                        "line_total": line_total,
                    })

                # -------- Создание чека --------
                sale_discount = int(request.POST.get("sale_discount", 0))

                sale = Sale.objects.create(
                    discount=sale_discount,
                    total=max(0, total - sale_discount),
                )

                # -------- Создание позиций --------
                for item in items_data:
                    sale_item = SaleItem.objects.create(
                        sale=sale,
                        sale_type=item["sale_type"],
                        perfume_id=item["perfume_id"],
                        cosmetic_id=item["cosmetic_id"],
                        ml=item["ml"],
                        bottles_count=item["bottles_count"],
                        bottle_count=item["atomizer_count"] if item["sale_type"] == "split" else item["bottles_count"],
                        bottle_type_id=item["bottle_type_id"],
                        unit_price=item["unit_price"],
                        discount=item["discount"],
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
            "error": error,
        }
    )


# =========================
# Печать чека
# =========================
def print_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    path = print_sale_receipt(sale.id)

    messages.success(request, f"Чек отправлен на печать ({path})")
    return redirect("sales_today")
