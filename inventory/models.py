from django.db import models
from products.models import Perfume, BottleType, CosmeticProduct

# Create your models here.

class PerfumeStock(models.Model):
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, verbose_name="Парфюм")
    received_bottles = models.PositiveIntegerField(default=0, help_text="Поступившие полные флаконы", verbose_name="Поступило (флаконы)")
    bottles_left = models.PositiveIntegerField(default=0, help_text="Остаток полных флаконов (целых)", verbose_name="Остаток флаконов")
    ml_left = models.FloatField(default=0.0, help_text="Остаток в мл во вскрытых флаконах (распив)", verbose_name="Остаток (мл)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Остаток парфюма"
        verbose_name_plural = "Остатки парфюма"

    def __str__(self):
        return f"Stock: {self.perfume} — {self.bottles_left} фл. / {self.ml_left} мл на распив"

class BottleStock(models.Model):
    bottle_type = models.ForeignKey(BottleType, on_delete=models.CASCADE, verbose_name="Тип тары")
    stock = models.PositiveIntegerField(default=0, help_text="Остаток данного вида бутылочек (штук)", verbose_name="Остаток (шт)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Остаток тары"
        verbose_name_plural = "Остатки тары"

    def __str__(self):
        return f"Tara: {self.bottle_type} — {self.stock} шт."

class CosmeticStock(models.Model):
    cosmetic = models.ForeignKey(CosmeticProduct, on_delete=models.CASCADE, verbose_name="Косметика")
    stock = models.PositiveIntegerField(default=0, help_text="Остаток поштучно", verbose_name="Остаток (шт)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Остаток косметики"
        verbose_name_plural = "Остатки косметики"

    def __str__(self):
        return f"Cosmetic stock: {self.cosmetic} — {self.stock} шт."
