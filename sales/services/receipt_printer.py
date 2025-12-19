from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sales.models import Sale


# =========================
# Инициализация принтера
# =========================
printer = None

try:
    from escpos.printer import Usb
    printer = Usb(0x0fe6, 0x811e)
    print(">>> ESC/POS PRINTER INITIALIZED")
except Exception as e:
    print(">>> PRINTER INIT ERROR:", e)
    printer = None


# =========================
# Печать чека
# =========================
def print_sale_receipt(sale_id: int) -> str:
    print(f">>> PRINT RECEIPT CALLED: sale_id={sale_id}")

    sale = Sale.objects.prefetch_related("items").get(id=sale_id)

    # ---- Параметры чека ----
    WIDTH = 384          # 58мм
    PADDING = 10
    LINE_HEIGHT = 28

    # ---- Шрифты ----
    font_big = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28
    )
    font_normal = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22
    )
    font_small = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20
    )

    lines: list[tuple[str, ImageFont.FreeTypeFont]] = []

    def add(text: str, font=font_normal):
        lines.append((text, font))

    # ---- Заголовок ----
    add("NOA BEAUTY SHOP", font_big)
    add("г. Бишкек, ул. Юнусалиева 177/2", font_small)
    add("+996 990 200 856", font_small)
    add(f"Чек № {sale.id}", font_small)
    add(sale.sale_date.strftime("%d.%m.%Y %H:%M"), font_small)
    add("-" * 32)

    # ---- Таблица ----
    COL1, COL2, COL3 = 16, 6, 8
    add(f"{'Товар':<{COL1}} {'Кол':<{COL2}} {'Сумма':<{COL3}}")
    add("-" * 32)

    for item in sale.items.all():
        if item.perfume:
            name = str(item.perfume)
            if item.sale_type == "split":
                qty = f"{item.ml}мл"
                if item.bottle_count:
                    qty += f"({item.bottle_count}ат)"
            else:
                qty = item.bottles_count
        elif item.cosmetic:
            name = str(item.cosmetic)
            qty = item.bottle_count
        else:
            name = "Товар"
            qty = 1

        line = f"{name[:COL1]:<{COL1}} {str(qty):<{COL2}} {item.line_total:<{COL3}}"
        add(line)

    # ---- Итоги ----
    add("-" * 32)
    add(f"ИТОГО: {sale.total} сом", font_big)

    if sale.discount:
        add(f"Скидка: {sale.discount} сом", font_small)

    add("-" * 32)
    add("Спасибо за покупку!", font_small)

    # ---- Рендер изображения ----
    height = PADDING * 2 + LINE_HEIGHT * len(lines)
    img = Image.new("L", (WIDTH, height), 255)
    draw = ImageDraw.Draw(img)

    y = PADDING
    for text, font in lines:
        draw.text((PADDING, y), text, font=font, fill=0)
        y += LINE_HEIGHT

    path = f"/tmp/receipt_{sale.id}.png"
    img.save(path)
    print(">>> RECEIPT IMAGE SAVED:", path)

    # ---- Печать ----
    if printer is None:
        print(">>> PRINTER IS NONE — PRINT SKIPPED")
    else:
        try:
            print(">>> SENDING IMAGE TO PRINTER")
            printer.image(path)
            printer.cut()
            print(">>> PRINT SUCCESS")
        except Exception as e:
            print(">>> PRINT ERROR:", e)

    return path
