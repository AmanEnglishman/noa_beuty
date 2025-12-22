from django.db import models

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Бренд")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name

class BottleType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название тары")
    volume_ml = models.PositiveIntegerField(help_text="Объем в мл", verbose_name="Объем (мл)")
    is_paid = models.BooleanField(default=False, help_text="Платная или бесплатная тара", verbose_name="Платная тара")
    price = models.PositiveIntegerField(default=0, help_text="Цена за флакон (если платный)", verbose_name="Цена (сом)")

    class Meta:
        verbose_name = "Тип тары"
        verbose_name_plural = "Типы тары"

    def __str__(self):
        return f"{self.name} ({self.volume_ml} мл)"

class Perfume(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="perfumes", verbose_name="Бренд")
    name = models.CharField(max_length=150, verbose_name="Название")
    barcode = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Штрихкод")
    bottle_volume_ml = models.PositiveIntegerField(help_text="Объем оригинального флакона в мл", verbose_name="Объем флакона (мл)")
    full_bottle_price = models.PositiveIntegerField(help_text="Цена за полный флакон, сом", verbose_name="Цена за флакон")
    price_per_ml = models.PositiveIntegerField(help_text="Цена за 1 мл, сом", verbose_name="Цена за 1 мл")

    class Meta:
        verbose_name = "Парфюм"
        verbose_name_plural = "Парфюмы"

    def __str__(self):
        return f"{self.brand.name} {self.name}"

class CosmeticProduct(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="cosmetics", verbose_name="Бренд")
    name = models.CharField(max_length=150, verbose_name="Название")
    barcode = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Штрихкод")
    unit_price = models.PositiveIntegerField(help_text="Цена за штуку, сом", verbose_name="Цена (сом)")
    stock = models.PositiveIntegerField(default=0, help_text="Остаток на складе, шт", verbose_name="Остаток (шт)")

    class Meta:
        verbose_name = "Косметика"
        verbose_name_plural = "Косметика"

    def __str__(self):
        return f"{self.brand.name} {self.name}"
