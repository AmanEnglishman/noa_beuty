from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sales.models import Sale

try:
    from escpos.printer import Usb
    printer = Usb(0x0fe6, 0x811e)
except Exception:
    printer = None


def print_sale_receipt(sale_id: int) -> str:
    sale = Sale.objects.prefetch_related("items").get(id=sale_id)

    WIDTH = 384
    PADDING = 10
    LINE_HEIGHT = 28

    font_big = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28
    )
    font_normal = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22
    )
    font_small = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20
    )

    lines = []

    def add(text, font=font_normal):
        lines.append((text, font))

    add("NOA BEAUTY SHOP", font_big)
    add("г. Бишкек, ул. Молодая 12", font_small)
    add("+996 555 123 456", font_small)
    add(f"Чек № {sale.id}", font_small)
    add(sale.sale_date.strftime("%d.%m.%Y %H:%M"), font_small)
    add("-" * 32)

    COL1, COL2, COL3 = 16, 6, 8
    add(f"{'Товар':<{COL1}} {'Кол':<{COL2}} {'Сумма':<{COL3}}")
    add("-" * 32)

    for item in sale.items.all():
        if item.perfume:
            name = f"{item.perfume}"
            qty = item.ml or item.bottles_count
        elif item.cosmetic:
            name = f"{item.cosmetic}"
            qty = item.bottle_count
        else:
            name = "Товар"
            qty = 1

        line = f"{name[:COL1]:<{COL1}} {qty:<{COL2}} {item.line_total:<{COL3}}"
        add(line)

    add("-" * 32)
    add(f"ИТОГО: {sale.total} сом", font_big)

    if sale.discount:
        add(f"Скидка на чек: {sale.discount} сом", font_small)

    add("-" * 32)
    add("Спасибо за покупку!", font_small)

    height = PADDING * 2 + LINE_HEIGHT * len(lines)
    img = Image.new("L", (WIDTH, height), 255)
    draw = ImageDraw.Draw(img)

    y = PADDING
    for text, font in lines:
        draw.text((PADDING, y), text, font=font, fill=0)
        y += LINE_HEIGHT

    path = f"/tmp/receipt_{sale.id}.png"
    img.save(path)

    if printer:
        try:
            printer.image(path)
            printer.cut()
        except Exception as e:
            print("Ошибка печати:", e)

    return path