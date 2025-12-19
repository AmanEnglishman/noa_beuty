import os
import django
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ----------------------------
# Настройка Django
# ----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # <-- путь к твоему settings
django.setup()

from sales.models import Sale

# ----------------------------
# Настройка принтера
# ----------------------------
try:
    from escpos.printer import Usb
    printer = Usb(0x0fe6, 0x811e)  # <-- замени VID/PID на твой принтер
except Exception as e:
    printer = None
    print(f"USB принтер недоступен: {e}")
    print("Чек будет сохранён только как PNG.")

# ----------------------------
# Шрифты и размеры
# ----------------------------
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

# ----------------------------
# Выбираем чек
# ----------------------------
sale = Sale.objects.prefetch_related("items").last()  # последний чек
if not sale:
    print("Нет продаж для печати.")
    exit()

# ----------------------------
# Формирование строк для чека
# ----------------------------
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

def fmt(name, qty, price):
    return f"{name[:COL1]:<{COL1}} {qty:<{COL2}} {price:<{COL3}}"

add(f"{'Товар':<{COL1}} {'Кол':<{COL2}} {'Сумма':<{COL3}}")
add("-" * 32)

for item in sale.items.all():
    if item.sale_type in ["split", "full"] and item.perfume:
        if item.sale_type == "split":
            name = f"{item.perfume.brand} {item.perfume.name} {item.ml}мл"
            qty = item.ml
        else:
            name = f"{item.perfume.brand} {item.perfume.name}"
            qty = item.bottles_count
    elif item.sale_type == "cosmetic" and item.cosmetic:
        name = f"{item.cosmetic.brand} {item.cosmetic.name}"
        qty = item.bottle_count
    else:
        name = "Неизвестный товар"
        qty = 0

    add(fmt(name, qty, item.line_total))

add("-" * 32)
add(f"ИТОГО: {sale.total} сом", font_big)

if sale.discount:
    add(f"Скидка на чек: {sale.discount} сом", font_small)

add("-" * 32)
add("Спасибо за покупку!", font_small)
add("Хорошего дня!", font_small)

# ----------------------------
# Генерация изображения
# ----------------------------
height = PADDING * 2 + LINE_HEIGHT * len(lines)
img = Image.new("L", (WIDTH, height), 255)
draw = ImageDraw.Draw(img)

y = PADDING
for text, font in lines:
    draw.text((PADDING, y), text, font=font, fill=0)
    y += LINE_HEIGHT

# Сохраняем PNG
receipt_file = f"/tmp/receipt_{sale.id}.png"
img.save(receipt_file)
print(f"Чек сохранён: {receipt_file}")

# ----------------------------
# Печать на USB принтере
# ----------------------------
if printer:
    try:
        printer.image(receipt_file)
        printer.cut()
        print("Чек отправлен на принтер.")
    except Exception as e:
        print(f"Ошибка при печати: {e}")
else:
    print("USB принтер недоступен. Чек сохранён как PNG.")