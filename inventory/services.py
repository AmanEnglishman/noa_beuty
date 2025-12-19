from django.db import transaction

from .models import PerfumeStock, BottleStock, CosmeticStock
from products.models import Perfume, BottleType, CosmeticProduct


def get_or_create_perfume_stock(perfume: Perfume) -> PerfumeStock:
    """
    Возвращает объект остатка по парфюму.
    Если записи нет (например, продали сразу, не занося приход), создаём с нулевыми остатками.
    """
    stock, _ = PerfumeStock.objects.get_or_create(
        perfume=perfume,
        defaults={
            "received_bottles": 0,
            "bottles_left": 0,
            "ml_left": 0,
        },
    )
    return stock


def get_or_create_bottle_stock(bottle_type: BottleType) -> BottleStock:
    stock, _ = BottleStock.objects.get_or_create(
        bottle_type=bottle_type,
        defaults={
            "stock": 0,
        },
    )
    return stock


def get_or_create_cosmetic_stock(cosmetic: CosmeticProduct) -> CosmeticStock:
    stock, _ = CosmeticStock.objects.get_or_create(
        cosmetic=cosmetic,
        defaults={
            "stock": 0,
        },
    )
    return stock


@transaction.atomic
def apply_sale_item_to_stocks(
    *,
    sale_type: str,
    perfume: Perfume | None = None,
    cosmetic: CosmeticProduct | None = None,
    bottle_type: BottleType | None = None,
    bottles_count: int = 0,
    ml: float = 0.0,
    bottle_count: int = 0,
) -> None:
    """
    Обновляет остатки склада в соответствии с одной позицией продажи.

    - full  : уменьшает количество полных флаконов парфюма
    - split : уменьшает остаток мл парфюма и количество тары
    - cosmetic : уменьшает остаток косметики (и при необходимости синхронизирует поле stock у продукта)
    """
    if sale_type == "full" and perfume and bottles_count > 0:
        perfume_stock = get_or_create_perfume_stock(perfume)
        perfume_stock.bottles_left = max(0, perfume_stock.bottles_left - bottles_count)
        perfume_stock.save(update_fields=["bottles_left", "updated_at"])

    elif sale_type == "split" and perfume:
        perfume_stock = get_or_create_perfume_stock(perfume)
        
        if ml > 0:
            # Получаем объем одного флакона парфюма
            bottle_volume_ml = perfume.bottle_volume_ml
            
            # Вычисляем необходимое количество мл
            ml_needed = float(ml)
            ml_available = perfume_stock.ml_left
            
            # Если недостаточно мл в открытых флаконах, открываем полные флаконы
            if ml_available < ml_needed:
                ml_deficit = ml_needed - ml_available
                # Вычисляем сколько полных флаконов нужно открыть
                bottles_to_open = int((ml_deficit + bottle_volume_ml - 1) // bottle_volume_ml)  # Округление вверх
                
                if bottles_to_open > 0:
                    # Проверяем, есть ли достаточно полных флаконов
                    if perfume_stock.bottles_left >= bottles_to_open:
                        # Открываем полные флаконы: уменьшаем bottles_left, увеличиваем ml_left
                        perfume_stock.bottles_left = max(0, perfume_stock.bottles_left - bottles_to_open)
                        perfume_stock.ml_left += bottles_to_open * bottle_volume_ml
                    else:
                        # Если недостаточно полных флаконов, открываем все что есть
                        bottles_to_open = perfume_stock.bottles_left
                        perfume_stock.ml_left += bottles_to_open * bottle_volume_ml
                        perfume_stock.bottles_left = 0
            
            # Теперь списываем необходимое количество мл
            perfume_stock.ml_left = max(0.0, perfume_stock.ml_left - ml_needed)
        
        perfume_stock.save(update_fields=["bottles_left", "ml_left", "updated_at"])

        if bottle_type and bottle_count > 0:
            bottle_stock = get_or_create_bottle_stock(bottle_type)
            bottle_stock.stock = max(0, bottle_stock.stock - bottle_count)
            bottle_stock.save(update_fields=["stock", "updated_at"])

    elif sale_type == "cosmetic" and cosmetic and bottle_count > 0:
        cosmetic_stock = get_or_create_cosmetic_stock(cosmetic)
        cosmetic_stock.stock = max(0, cosmetic_stock.stock - bottle_count)
        cosmetic_stock.save(update_fields=["stock", "updated_at"])

        # По желанию поддерживаем синхронизацию агрегированного остатка в продукте
        if hasattr(cosmetic, "stock"):
            cosmetic.stock = max(0, (cosmetic.stock or 0) - bottle_count)
            cosmetic.save(update_fields=["stock"])


