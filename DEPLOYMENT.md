# CRM Nice - Deployment Guide

## Деплой на Render

### Автоматичний деплой через render.yaml

Проєкт налаштований для автоматичного деплою на Render з використанням `render.yaml`.

### Кроки для деплою:

1. **Підключіть репозиторій до Render:**
   - Зайдіть на [Render Dashboard](https://dashboard.render.com/)
   - Натисніть "New +" → "Blueprint"
   - Підключіть GitHub репозиторій `git@github.com:BonisOleg/odessa.git`
   - Render автоматично виявить `render.yaml` і створить сервіси

2. **Налаштуйте змінні середовища:**
   
   Render автоматично створить більшість змінних, але перевірте:
   - `SECRET_KEY` - буде згенеровано автоматично
   - `DATABASE_URL` - буде підключено до PostgreSQL бази
   - `ALLOWED_HOSTS` - додайте ваш домен (наприклад: `your-app.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS` - додайте `https://your-app.onrender.com`

3. **Деплой відбудеться автоматично:**
   - Render запустить `build.sh`
   - Виконає міграції
   - Зберить статичні файли
   - Запустить Gunicorn

### Ручний деплой (альтернатива)

Якщо ви хочете створити сервіс вручну:

1. Створіть новий Web Service на Render
2. Підключіть репозиторій
3. Налаштування:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn CRM_Nice.wsgi:application`
   - **Environment:** Python 3

### Локальна розробка

1. Клонуйте репозиторій:
```bash
git clone git@github.com:BonisOleg/odessa.git
cd odessa
```

2. Створіть віртуальне середовище:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Встановіть залежності:
```bash
pip install -r requirements.txt
```

4. Створіть `.env` файл (використайте `.env.example` як шаблон):
```bash
cp .env.example .env
```

5. Виконайте міграції:
```bash
python manage.py migrate
```

6. Створіть суперюзера:
```bash
python manage.py createsuperuser
```

7. Запустіть сервер розробки:
```bash
python manage.py runserver
```

### Структура проєкту

- `CRM_Nice/` - основний Django проєкт
  - `settings/` - налаштування розділені за середовищами
    - `base.py` - базові налаштування
    - `develop.py` - локальна розробка
    - `production.py` - production на Render
    - `test.py` - тестування
- `myapp/` - основний додаток
- `templates/` - HTML шаблони
- `static/` - статичні файли (CSS, JS)
- `build.sh` - скрипт збірки для Render
- `render.yaml` - конфігурація Render Blueprint

### Технології

- Django 5.0+
- PostgreSQL (production)
- SQLite (development)
- WhiteNoise (статичні файли)
- Gunicorn (WSGI сервер)
- HTMX 2.0.8 (динамічний UI)
- Vanilla JS (без jQuery)

### Безпека

Production налаштування включають:
- SSL redirect
- Secure cookies
- HSTS
- XSS protection
- Content-Type nosniff
- CSP headers

### Підтримка

Для питань та проблем створіть issue в GitHub репозиторії.

