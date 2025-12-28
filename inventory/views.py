from django_filters.views import FilterView
from django.shortcuts import render
from .models import PerfumeStock, BottleStock, CosmeticStock
from .filters import (
    PerfumeStockFilter,
    BottleStockFilter,
    CosmeticStockFilter
)
from sales.models import SaleItem

class PerfumeStockListView(FilterView):
    model = PerfumeStock
    template_name = "inventory/perfume_stock_list.html"
    filterset_class = PerfumeStockFilter
    context_object_name = "stocks"

class BottleStockListView(FilterView):
    model = BottleStock
    template_name = "inventory/bottle_stock_list.html"
    filterset_class = BottleStockFilter
    context_object_name = "stocks"

class CosmeticStockListView(FilterView):
    model = CosmeticStock
    template_name = "inventory/cosmetic_stock_list.html"
    filterset_class = CosmeticStockFilter
    context_object_name = "stocks"

def SplitSalesListView(request):
    # Показать все распивы
    split_items = SaleItem.objects.filter(sale_type="split").select_related("sale", "perfume", "bottle_type")
    return render(request, "inventory/split_sales_list.html", {"split_items": split_items})

def inventory_hub(request):
    return render(request, 'inventory/hub.html')
