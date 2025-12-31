from django.contrib import admin
from .models import Sale, SaleItem, Expense, Income, PaymentMethod

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "sale_date", "discount_percent", "total")
    inlines = [SaleItemInline]
    date_hierarchy = "sale_date"


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sale_type",
        "bottles_count",
        "ml",
        "unit_price",
        "line_total",
        "discount_percent",
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "description", "amount")
    search_fields = ("description",)


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "description", "amount")
    search_fields = ("description",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass
