#!/bin/sh

# Создаем миграции
echo "Creating migrations.."
python3 manage.py makemigrations

# Применяем миграции
echo "Running migrations..."
python3 manage.py migrate

# Создаем публичный тенант проекта
echo "Creating public tenant..."
python3 manage.py init_tenant || true

# Заполняем БД тестовыми данными
echo "Creating public tenant..."
python3 manage.py import_test_data || true

# Запускаем сервер, заменяя текущий процесс
echo "Starting server..."
gunicorn --bind 0.0.0.0:8000 banking_api.wsgi:application --reload