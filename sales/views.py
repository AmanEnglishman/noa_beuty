from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Sale, SaleItem
from products.models import Perfume, BottleType, CosmeticProduct

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
                SaleItem.objects.create(
                    sale=sale_obj,
                    sale_type=item['type'],
                    perfume_id=item['perfume_id'] or None,
                    cosmetic_id=item['cosmetic_id'] or None,
                    ml=item['ml'],
                    bottles_count=item['bottles_count'],
                    bottle_type_id=item['bottle_type_id'] or None,
                    bottle_count=item['bottles_count'], # для косметики аналогично
                    unit_price=item['price'],
                    discount=item['item_discount'],
                    line_total=item['line_total']
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
