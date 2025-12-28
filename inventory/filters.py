import django_filters
from .models import PerfumeStock, BottleStock, CosmeticStock
from sales.models import SaleItem
from products.models import Perfume, Brand, BottleType


class PerfumeStockFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="perfume__name",
        lookup_expr="icontains",
        label="Название парфюма"
    )
    bottles_min = django_filters.NumberFilter(
        field_name="bottles_left",
        lookup_expr="gte",
        label="Минимум флаконов"
    )
    bottles_max = django_filters.NumberFilter(
        field_name="bottles_left",
        lookup_expr="lte",
        label="Максимум флаконов"
    )
    ml_min = django_filters.NumberFilter(
        field_name="ml_left",
        lookup_expr="gte",
        label="Минимум мл"
    )
    ml_max = django_filters.NumberFilter(
        field_name="ml_left",
        lookup_expr="lte",
        label="Максимум мл"
    )

    class Meta:
        model = PerfumeStock
        fields = []


class BottleStockFilter(django_filters.FilterSet):
    bottle_name = django_filters.CharFilter(
        field_name="bottle__name",
        lookup_expr="icontains",
        label="Название флакона"
    )
    count_min = django_filters.NumberFilter(
        field_name="count",
        lookup_expr="gte",
        label="Минимум количества"
    )
    count_max = django_filters.NumberFilter(
        field_name="count",
        lookup_expr="lte",
        label="Максимум количества"
    )

    class Meta:
        model = BottleStock
        fields = []


class CosmeticStockFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="cosmetic__name",
        lookup_expr="icontains",
        label="Название косметики"
    )
    count_min = django_filters.NumberFilter(
        field_name="count",
        lookup_expr="gte",
        label="Минимум"
    )
    count_max = django_filters.NumberFilter(
        field_name="count",
        lookup_expr="lte",
        label="Максимум"
    )

    class Meta:
        model = CosmeticStock
        fields = []


class SplitSalesFilter(django_filters.FilterSet):
    perfume = django_filters.ModelChoiceFilter(
        queryset=Perfume.objects.select_related('brand').all().order_by('brand__name', 'name'),
        label="Парфюм"
    )
    brand = django_filters.ModelChoiceFilter(
        field_name="perfume__brand",
        queryset=Brand.objects.all().order_by('name'),
        label="Бренд"
    )
    perfume_name = django_filters.CharFilter(
        field_name="perfume__name",
        lookup_expr="icontains",
        label="Название парфюма (поиск)"
    )
    date_from = django_filters.DateFilter(
        field_name="sale__sale_date__date",
        lookup_expr="gte",
        label="Дата от"
    )
    date_to = django_filters.DateFilter(
        field_name="sale__sale_date__date",
        lookup_expr="lte",
        label="Дата до"
    )
    ml_min = django_filters.NumberFilter(
        field_name="ml",
        lookup_expr="gte",
        label="Мл от"
    )
    ml_max = django_filters.NumberFilter(
        field_name="ml",
        lookup_expr="lte",
        label="Мл до"
    )
    bottle_type = django_filters.ModelChoiceFilter(
        queryset=BottleType.objects.all().order_by('name'),
        label="Тип атомайзеров"
    )

    class Meta:
        model = SaleItem
        fields = []
