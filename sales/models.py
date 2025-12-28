from django.db import models
from products.models import Perfume, BottleType, CosmeticProduct
from inventory.models import BottleStock

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    method_type = models.CharField(
        max_length=100,
        verbose_name="Тип оплаты"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"

    def __str__(self):
        return self.name


class Sale(models.Model):
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи")
    discount_percent = models.PositiveSmallIntegerField(default=0, help_text="Скидка на чек (%)", verbose_name="Скидка на чек (%)")

    total = models.PositiveIntegerField(default=0, help_text="Итоговая сумма чека, сом", verbose_name="Итоговая сумма")

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        verbose_name="Способ оплаты",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"

    def __str__(self):
        return f"Sale #{self.pk} — {self.sale_date.date()}"

class SaleItem(models.Model):

    SALE_TYPE_CHOICES = [
        ('full', 'Флакон полностью'),
        ('split', 'Распив'),
        ('cosmetic', 'Косметика'),
        ('gift', 'Подарок'),
    ]
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items", verbose_name="Чек")
    sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES, verbose_name="Тип продажи")
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Парфюм")
    cosmetic = models.ForeignKey(CosmeticProduct, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Косметика")
    bottles_count = models.PositiveIntegerField(default=0, help_text="Флаконов (для продажи целиком)", verbose_name="Количество флаконов")
    ml = models.FloatField(default=0, help_text="Количество мл (для распива)", verbose_name="Количество (мл)")
    bottle_type = models.ForeignKey(BottleType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Тип атомайзеров")
    bottle_count = models.PositiveIntegerField(default=0, help_text="Тара на распив (шт)", verbose_name="Количество тары (шт)")
    unit_price = models.PositiveIntegerField(help_text="Цена за 1 мл или 1 ед.", verbose_name="Цена за ед./мл")
    discount_percent = models.PositiveSmallIntegerField(default=0, help_text="Скидка на позицию (%)", verbose_name="Скидка (%)")
    line_total = models.PositiveIntegerField(help_text="Сумма позиции, сом", verbose_name="Сумма строки")

    class Meta:
        verbose_name = "Позиция в чеке"
        verbose_name_plural = "Позиции в чеке"

    def __str__(self):
        if self.sale_type == 'full':
            return f"{self.perfume} x {self.bottles_count}"
        elif self.sale_type == 'split':
            return f"{self.perfume} x {self.ml} ml"
        elif self.sale_type == 'gift':
            if self.perfume:
                if self.bottles_count > 0:
                    return f"{self.perfume} x {self.bottles_count} (Подарок)"
                else:
                    return f"{self.perfume} x {self.ml} ml (Подарок)"
            elif self.cosmetic:
                return f"{self.cosmetic} x {self.bottle_count} (Подарок)"
            else:
                return "Подарок"
        else:
            return f"{self.cosmetic} x {self.bottle_count}"

class Expense(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата расхода")
    description = models.CharField(max_length=255, verbose_name="Описание")
    amount = models.PositiveIntegerField(help_text="Сумма расхода, сом", verbose_name="Сумма (сом)")

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def __str__(self):
        return f"Расход: {self.description} - {self.amount} сом"

class Income(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата дохода")
    description = models.CharField(max_length=255, verbose_name="Описание")
    amount = models.PositiveIntegerField(help_text="Сумма дохода, сом", verbose_name="Сумма (сом)")

    class Meta:
        verbose_name = "Доход"
        verbose_name_plural = "Доходы"

    def __str__(self):
        return f"Доход: {self.description} - {self.amount} сом"



class PrintQueue(models.Model):
    sale = models.ForeignKey("Sale", on_delete=models.CASCADE)
    printed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Print sale {self.sale_id} | printed={self.printed}"
