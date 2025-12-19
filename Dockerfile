FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей Python
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директорий для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

# Установка прав
RUN chmod +x /app/manage.py

# Открываем порт
EXPOSE 8000

# Команда по умолчанию (переопределяется в docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]