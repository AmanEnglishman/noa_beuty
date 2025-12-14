from django.urls import path
from .views import (
    PerfumeStockListView,
    BottleStockListView,
    CosmeticStockListView
)

urlpatterns = [
    path("perfume/", PerfumeStockListView.as_view(), name="perfume-stock"),
    path("bottle/", BottleStockListView.as_view(), name="bottle-stock"),
    path("cosmetic/", CosmeticStockListView.as_view(), name="cosmetic-stock"),
]
