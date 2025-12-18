#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Створення тестового користувача для логіну (якщо ще не існує)
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model

User = get_user_model()
username = "demo"
password = "Demo1234!"
email = "demo@example.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, password=password, email=email)
    print(f"Created demo user: {username} / {password}")
else:
    print(f"Demo user already exists: {username}")
EOF
