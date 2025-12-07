from django.contrib import admin
from .models import PerfumeStock, BottleStock, CosmeticStock

@admin.register(PerfumeStock)
class PerfumeStockAdmin(admin.ModelAdmin):
    list_display = ("id", "perfume", "received_bottles", "bottles_left", "ml_left", "updated_at")
    search_fields = ("perfume__name",)

@admin.register(BottleStock)
class BottleStockAdmin(admin.ModelAdmin):
    list_display = ("id", "bottle_type", "stock", "updated_at")

@admin.register(CosmeticStock)
class CosmeticStockAdmin(admin.ModelAdmin):
    list_display = ("id", "cosmetic", "stock", "updated_at")
    search_fields = ("cosmetic__name",)
