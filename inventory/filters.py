import django_filters
from .models import PerfumeStock, BottleStock, CosmeticStock


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
