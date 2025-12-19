# Быстрый старт - Команды для деплоя

## Первоначальная настройка на сервере

```bash
# 1. Установка Docker и Docker Compose (если не установлены)
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 2. Клонирование/загрузка проекта
cd /opt
git clone <your-repo> noa_beuty  # или загрузите через SCP
cd noa_beuty

# 3. Настройка переменных окружения
cp .env.example .env
nano .env  # Отредактируйте SECRET_KEY, ALLOWED_HOSTS, POSTGRES_PASSWORD

# 4. Генерация SECRET_KEY (выполните на сервере или локально)
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 5. Сборка и запуск
docker-compose build
docker-compose up -d

# 6. Создание суперпользователя
docker-compose exec django python manage.py createsuperuser
```

## Основные команды управления

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f django
docker-compose logs -f nginx

# Статус контейнеров
docker-compose ps

# Выполнение миграций
docker-compose exec django python manage.py migrate

# Сбор статики
docker-compose exec django python manage.py collectstatic --noinput
```

## Обновление проекта

```bash
cd /opt/noa_beuty
docker-compose down
git pull  # или загрузите новые файлы
docker-compose build
docker-compose up -d
docker-compose exec django python manage.py migrate
```

## Резервное копирование БД

```bash
# Создание бэкапа
docker-compose exec db pg_dump -U noa_user noa_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
docker-compose exec -T db psql -U noa_user noa_db < backup_20240101_120000.sql
```

## Проверка работы

```bash
# Проверка доступности
curl http://localhost:8000

# Проверка логов
docker-compose logs --tail=50 django
```

