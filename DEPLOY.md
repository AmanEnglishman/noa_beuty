# Инструкция по развёртыванию проекта NOA Beauty на сервере

## Требования

- Сервер с Ubuntu 20.04+ или аналогичный Linux
- Docker и Docker Compose установлены
- Минимум 2GB RAM, 20GB свободного места на диске

## Шаг 1: Подготовка сервера

### Установка Docker и Docker Compose

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагрузка сессии (или перелогиниться)
newgrp docker
```

### Проверка установки

```bash
docker --version
docker-compose --version
```

## Шаг 2: Загрузка проекта на сервер

### Вариант A: Через Git (рекомендуется)

```bash
# Клонирование репозитория
cd /opt
sudo git clone <your-repository-url> noa_beuty
cd noa_beuty
sudo chown -R $USER:$USER .
```

### Вариант B: Через SCP

```bash
# На локальной машине
scp -r /path/to/noa_beuty user@server:/opt/
```

## Шаг 3: Настройка переменных окружения

```bash
cd /opt/noa_beuty

# Создание файла .env из примера
cp .env.example .env

# Редактирование .env файла
nano .env
```

**Важно изменить в `.env`:**
- `SECRET_KEY` - сгенерируйте новый секретный ключ Django
- `ALLOWED_HOSTS` - укажите ваш домен или IP сервера
- `POSTGRES_PASSWORD` - установите надёжный пароль для БД
- `DEBUG=False` - для production

**Генерация SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Шаг 4: Сборка и запуск контейнеров

```bash
cd /opt/noa_beuty

# Сборка образов
docker-compose build

# Запуск контейнеров в фоновом режиме
docker-compose up -d

# Просмотр логов (для проверки)
docker-compose logs -f django
```

## Шаг 5: Создание суперпользователя

```bash
# Вход в контейнер Django
docker-compose exec django python manage.py createsuperuser

# Следуйте инструкциям для создания админа
```

## Шаг 6: Проверка работы

```bash
# Проверка статуса контейнеров
docker-compose ps

# Проверка логов
docker-compose logs django
docker-compose logs nginx

# Проверка доступности
curl http://localhost:8000
```

## Полезные команды для управления

### Остановка контейнеров
```bash
docker-compose down
```

### Перезапуск контейнеров
```bash
docker-compose restart
```

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Только Django
docker-compose logs -f django

# Только Nginx
docker-compose logs -f nginx
```

### Выполнение команд Django
```bash
# Миграции
docker-compose exec django python manage.py migrate

# Создание суперпользователя
docker-compose exec django python manage.py createsuperuser

# Сбор статики
docker-compose exec django python manage.py collectstatic --noinput

# Django shell
docker-compose exec django python manage.py shell
```

### Обновление проекта

```bash
cd /opt/noa_beuty

# Остановка контейнеров
docker-compose down

# Обновление кода (если через Git)
git pull

# Пересборка образов
docker-compose build

# Запуск с миграциями
docker-compose up -d
docker-compose exec django python manage.py migrate
```

### Резервное копирование базы данных

```bash
# Создание бэкапа
docker-compose exec db pg_dump -U noa_user noa_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
docker-compose exec -T db psql -U noa_user noa_db < backup_20240101_120000.sql
```

## Настройка Nginx для домена (опционально)

Если у вас есть домен, создайте файл `/etc/nginx/sites-available/noa_beuty`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:
```bash
sudo ln -s /etc/nginx/sites-available/noa_beuty /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

После получения SSL-сертификата обновите `.env`:
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

И перезапустите:
```bash
docker-compose restart django
```

## Мониторинг и обслуживание

### Проверка использования ресурсов
```bash
docker stats
```

### Очистка неиспользуемых образов
```bash
docker system prune -a
```

### Просмотр размера volumes
```bash
docker system df -v
```

## Устранение проблем

### Контейнер не запускается
```bash
# Проверка логов
docker-compose logs django

# Проверка конфигурации
docker-compose config
```

### Проблемы с базой данных
```bash
# Проверка подключения к БД
docker-compose exec db psql -U noa_user -d noa_db -c "SELECT version();"
```

### Проблемы со статикой
```bash
# Пересборка статики
docker-compose exec django python manage.py collectstatic --noinput --clear
```

## Контакты и поддержка

При возникновении проблем проверьте:
1. Логи контейнеров: `docker-compose logs`
2. Статус контейнеров: `docker-compose ps`
3. Конфигурацию: `docker-compose config`

