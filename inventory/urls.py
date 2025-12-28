from django.urls import path
from .views import (
    PerfumeStockListView,
    BottleStockListView,
    CosmeticStockListView,
    inventory_hub,
    SplitSalesListView,
)

urlpatterns = [
    path('', inventory_hub, name='inventory-hub'),
    path("perfume/", PerfumeStockListView.as_view(), name="perfume-stock"),
    path("bottle/", BottleStockListView.as_view(), name="bottle-stock"),
    path("cosmetic/", CosmeticStockListView.as_view(), name="cosmetic-stock"),
    path("split/", SplitSalesListView.as_view(), name="split-sales"),
]
