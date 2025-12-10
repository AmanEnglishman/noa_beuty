from django_filters.views import FilterView
from .models import PerfumeStock, BottleStock, CosmeticStock
from .filters import (
    PerfumeStockFilter,
    BottleStockFilter,
    CosmeticStockFilter
)


class PerfumeStockListView(FilterView):
    model = PerfumeStock
    template_name = "perfume_stock_list.html"
    filterset_class = PerfumeStockFilter
    context_object_name = "stocks"


class BottleStockListView(FilterView):
    model = BottleStock
    template_name = "bottle_stock_list.html"
    filterset_class = BottleStockFilter
    context_object_name = "stocks"


class CosmeticStockListView(FilterView):
    model = CosmeticStock
    template_name = "cosmetic_stock_list.html"
    filterset_class = CosmeticStockFilter
    context_object_name = "stocks"
