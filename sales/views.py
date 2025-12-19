from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import Sale, SaleItem
from products.models import Perfume, BottleType, CosmeticProduct
from inventory.services import apply_sale_item_to_stocks
from django.contrib import messages
from .services.receipt_printer import print_sale_receipt
# Create your views here.

def sales_today(request):
    today = timezone.localdate()
    sales = Sale.objects.filter(sale_date__date=today).prefetch_related('items')
    return render(request, 'sales/sales_today.html', {'sales': sales, 'today': today})

def sale_create(request):
    perfumes = Perfume.objects.select_related('brand').all()
    bottles = BottleType.objects.all()
    cosmetics = CosmeticProduct.objects.all()
    error = None

    if request.method == 'POST':
        # Считываем все позиции из динамической формы
        try:
            with transaction.atomic():
                items = []
                types = request.POST.getlist('item_type')
                perfumes_ids = request.POST.getlist('perfume')
                cosmetics_ids = request.POST.getlist('cosmetic')
                ml_qties = request.POST.getlist('ml_qty')
                bottle_qties = request.POST.getlist('bottle_qty')
                bottle_type_ids = request.POST.getlist('bottle_type')
                prices = request.POST.getlist('price')
                item_discounts = request.POST.getlist('item_discount')
                total = 0

                for i in range(len(types)):
                    type_ = types[i]
                    perfume_id = perfumes_ids[i] if i < len(perfumes_ids) and perfumes_ids[i] else None
                    cosmetic_id = cosmetics_ids[i] if i < len(cosmetics_ids) and cosmetics_ids[i] else None
                    ml = float(ml_qties[i]) if (i < len(ml_qties) and ml_qties[i]) else 0
                    bottles_count = int(bottle_qties[i]) if (i < len(bottle_qties) and bottle_qties[i]) else 0
                    bottle_type_id = bottle_type_ids[i] if i < len(bottle_type_ids) and bottle_type_ids[i] else None
                    price = int(prices[i]) if i < len(prices) and prices[i] else 0
                    item_discount = int(item_discounts[i]) if i < len(item_discounts) and item_discounts[i] else 0
                    qty = ml if type_ == 'split' else bottles_count if type_ in ('full', 'cosmetic') else 1
                    line_total = max(0, price * qty - item_discount)
                    total += line_total
                    items.append({
                        'type': type_, 'perfume_id': perfume_id, 'cosmetic_id': cosmetic_id,
                        'ml': ml, 'bottles_count': bottles_count, 'bottle_type_id': bottle_type_id,
                        'price': price, 'item_discount': item_discount, 'line_total': line_total
                    })

                sale_discount = int(request.POST.get('sale_discount', 0))
                sale_obj = Sale.objects.create(discount=sale_discount, total=max(0, total - sale_discount))

                for item in items:
                    sale_item = SaleItem.objects.create(
                        sale=sale_obj,
                        sale_type=item['type'],
                        perfume_id=item['perfume_id'] or None,
                        cosmetic_id=item['cosmetic_id'] or None,
                        ml=item['ml'],
                        bottles_count=item['bottles_count'],
                        bottle_type_id=item['bottle_type_id'] or None,
                        bottle_count=item['bottles_count'],  # для косметики аналогично
                        unit_price=item['price'],
                        discount=item['item_discount'],
                        line_total=item['line_total']
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

            return redirect('sales_today')
        except Exception as e:
            error = f"Ошибка при сохранении: {e}"

    return render(request, 'sales/sale_create.html', {
        'perfumes': perfumes,
        'bottles': bottles,
        'cosmetics': cosmetics,
        'error': error
    })


def print_sale(request, sale_id):
    print(">>> PRINTING SALE", sale_id)

    path = print_sale_receipt(sale_id)

    messages.success(request, f"Чек сохранён: {path}")
    return redirect("sales_today")


# from django.shortcuts import render, redirect
# from django.utils import timezone
# from django.db import transaction

# from .models import Sale, SaleItem
# from products.models import Perfume, BottleType, CosmeticProduct
# from inventory.services import apply_sale_item_to_stocks

# # Create your views here.

# def sales_today(request):
#     today = timezone.localdate()
#     sales = Sale.objects.filter(sale_date__date=today).prefetch_related('items')
#     return render(request, 'sales/sales_today.html', {'sales': sales, 'today': today})

# def sale_create(request):
#     perfumes = Perfume.objects.select_related('brand').all()
#     bottles = BottleType.objects.all()
#     cosmetics = CosmeticProduct.objects.all()
#     error = None

#     if request.method == 'POST':
#         # Считываем все позиции из динамической формы
#         try:
#             with transaction.atomic():
#                 items = []
#                 types = request.POST.getlist('item_type')
#                 perfumes_ids = request.POST.getlist('perfume')
#                 cosmetics_ids = request.POST.getlist('cosmetic')
#                 ml_qties = request.POST.getlist('ml_qty')
#                 bottle_qties = request.POST.getlist('bottle_qty')
#                 bottle_type_ids = request.POST.getlist('bottle_type')
#                 prices = request.POST.getlist('price')
#                 item_discounts = request.POST.getlist('item_discount')
#                 total = 0

#                 for i in range(len(types)):
#                     type_ = types[i]
#                     perfume_id = perfumes_ids[i] if i < len(perfumes_ids) and perfumes_ids[i] else None
#                     cosmetic_id = cosmetics_ids[i] if i < len(cosmetics_ids) and cosmetics_ids[i] else None
#                     ml = float(ml_qties[i]) if (i < len(ml_qties) and ml_qties[i]) else 0
#                     bottles_count = int(bottle_qties[i]) if (i < len(bottle_qties) and bottle_qties[i]) else 0
#                     bottle_type_id = bottle_type_ids[i] if i < len(bottle_type_ids) and bottle_type_ids[i] else None
#                     price = int(prices[i]) if i < len(prices) and prices[i] else 0
#                     item_discount = int(item_discounts[i]) if i < len(item_discounts) and item_discounts[i] else 0
#                     qty = ml if type_ == 'split' else bottles_count if type_ in ('full', 'cosmetic') else 1
#                     line_total = max(0, price * qty - item_discount)
#                     total += line_total
#                     items.append({
#                         'type': type_, 'perfume_id': perfume_id, 'cosmetic_id': cosmetic_id,
#                         'ml': ml, 'bottles_count': bottles_count, 'bottle_type_id': bottle_type_id,
#                         'price': price, 'item_discount': item_discount, 'line_total': line_total
#                     })

#                 sale_discount = int(request.POST.get('sale_discount', 0))
#                 sale_obj = Sale.objects.create(discount=sale_discount, total=max(0, total - sale_discount))

#                 for item in items:
#                     sale_item = SaleItem.objects.create(
#                         sale=sale_obj,
#                         sale_type=item['type'],
#                         perfume_id=item['perfume_id'] or None,
#                         cosmetic_id=item['cosmetic_id'] or None,
#                         ml=item['ml'],
#                         bottles_count=item['bottles_count'],
#                         bottle_type_id=item['bottle_type_id'] or None,
#                         bottle_count=item['bottles_count'],  # для косметики аналогично
#                         unit_price=item['price'],
#                         discount=item['item_discount'],
#                         line_total=item['line_total']
#                     )

#                     apply_sale_item_to_stocks(
#                         sale_type=sale_item.sale_type,
#                         perfume=sale_item.perfume,
#                         cosmetic=sale_item.cosmetic,
#                         bottle_type=sale_item.bottle_type,
#                         bottles_count=sale_item.bottles_count,
#                         ml=sale_item.ml,
#                         bottle_count=sale_item.bottle_count,
#                     )

#             return redirect('sales_today')
#         except Exception as e:
#             error = f"Ошибка при сохранении: {e}"

#     return render(request, 'sales/sale_create.html', {
#         'perfumes': perfumes,
#         'bottles': bottles,
#         'cosmetics': cosmetics,
#         'error': error
#     })
