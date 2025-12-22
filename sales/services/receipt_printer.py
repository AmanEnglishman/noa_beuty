# sales/services/receipt_renderer.py

import os
import io
from PIL import Image, ImageDraw, ImageFont
from sales.models import Sale

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

FONT_REGULAR = os.path.join(BASE_DIR, "fonts", "DejaVuSans.ttf")
FONT_BOLD = os.path.join(BASE_DIR, "fonts", "DejaVuSans-Bold.ttf")


def load_fonts():
    return {
        "title": ImageFont.truetype(FONT_BOLD, 30),
        "bold": ImageFont.truetype(FONT_BOLD, 24),
        "normal": ImageFont.truetype(FONT_REGULAR, 22),
        "small": ImageFont.truetype(FONT_REGULAR, 20),
    }


def clean_item_name(name: str) -> str:
    return (
        name.replace("Split:", "")
            .replace("мл", "")
            .strip()
    )


def render_sale_receipt_png(sale_id: int) -> bytes:
    sale = Sale.objects.prefetch_related("items").get(id=sale_id)

    fonts = load_fonts()

    WIDTH = 384  # 58 мм
    PADDING = 12
    LINE_HEIGHT = 30
    RIGHT_COL_X = WIDTH - PADDING

    lines = []

    def add(text, font, align="left"):
        lines.append((text, font, align))

    # ===== HEADER =====
    add("NOA BEAUTY", fonts["title"], "center")
    add("г. Бишкек, ул. Юнусалиева 177/2", fonts["small"], "center")
    add("+996 990 20 08 56", fonts["small"], "center")
    add("-" * 32, fonts["small"], "center")

    add(f"Чек № {sale.id}", fonts["small"])
    add(sale.sale_date.strftime("%d.%m.%Y  %H:%M"), fonts["small"])
    add("-" * 32, fonts["small"], "center")

    # ===== ITEMS =====
    for item in sale.items.all():

    # ---- NAME ----
        if item.sale_type in ("full", "split"):
            name = str(item.perfume)
        else:
            name = str(item.cosmetic)

        name = clean_item_name(name)
        add(name[:32], fonts["normal"])

        # ---- QTY ----
        if item.sale_type == "full":
            qty = item.bottles_count
            qty_text = f"{qty} шт"
        elif item.sale_type == "split":
            qty = item.ml
            qty_text = f"{qty:g} мл"
        else:
            qty = item.bottle_count
            qty_text = f"{qty} шт"

        # ---- PRICE ----
        price = item.unit_price

        # ---- BASE TOTAL (БЕЗ СКИДКИ) ----
        base_total = round(price * qty)

        # ---- DISCOUNT SUM ----
        discount_sum = round(
            base_total * item.discount_percent / 100
        )

        # ---- строка: количество × цена | БАЗОВАЯ сумма ----
        left = f"{qty_text} × {price}"
        right = f"{base_total}"

        lines.append((left, fonts["small"], "left-right", right))

        # ---- строка скидки ----
        if item.discount_percent > 0:
            discount_left = f"Скидка {item.discount_percent}%"
            discount_right = f"-{discount_sum}"

            lines.append(
                (discount_left, fonts["small"], "left-right", discount_right)
            )

    add("-" * 32, fonts["small"], "center")

    # ===== CHECK DISCOUNT =====
    if sale.discount_percent > 0:
        items_total = sum(i.line_total for i in sale.items.all())
        sale_discount_sum = round(
            items_total * sale.discount_percent / 100
        )
        add(
            f"Скидка на чек {sale.discount_percent}%",
            fonts["small"],
            "center",
        )
        add(f"-{sale_discount_sum} сом", fonts["small"], "center")
        add("-" * 32, fonts["small"], "center")

    # ===== TOTAL =====
    add("ИТОГО", fonts["bold"], "center")
    add(f"{sale.total} сом", fonts["title"], "center")

    add("-" * 32, fonts["small"], "center")
    add("Твоя лучшая покупка за сегодня!", fonts["small"], "center")

    # ===== RENDER =====
    height = PADDING * 2 + LINE_HEIGHT * len(lines)
    img = Image.new("L", (WIDTH, height), 255)
    draw = ImageDraw.Draw(img)

    y = PADDING
    for line in lines:
        if len(line) == 3:
            text, font, align = line
            if align == "center":
                w = draw.textlength(text, font=font)
                x = (WIDTH - w) // 2
            else:
                x = PADDING
            draw.text((x, y), text, fill=0, font=font)
        else:
            left, font, _, right = line
            draw.text((PADDING, y), left, fill=0, font=font)
            w = draw.textlength(right, font=font)
            draw.text((RIGHT_COL_X - w, y), right, fill=0, font=font)
        y += LINE_HEIGHT

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
