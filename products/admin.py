from django.contrib import admin
from .models import Brand, BottleType, Perfume, CosmeticProduct

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(BottleType)
class BottleTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "volume_ml", "is_paid", "price")
    list_filter = ("is_paid",)

@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "name", "bottle_volume_ml", "full_bottle_price", "price_per_ml")
    search_fields = ("name",)
    list_filter = ("brand",)

@admin.register(CosmeticProduct)
class CosmeticProductAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "name", "unit_price", )
    search_fields = ("name",)
    list_filter = ("brand",)
