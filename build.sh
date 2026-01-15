#!/usr/bin/env bash
# exit on error
set -o errexit

echo "⚠️  WARNING: Render uses ephemeral filesystem!"
echo "Media files (logos, photos) will be LOST after each deploy."
echo "For production, configure S3/Cloudinary for persistent storage."
echo ""

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Створення тестового користувача для логіну (якщо ще не існує)
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from myapp.models import UserProfile

User = get_user_model()
username = "demo"
password = "Demo1234!"
email = "demo@example.com"

user, created = User.objects.get_or_create(
    username=username,
    defaults={'email': email, 'is_staff': True, 'is_superuser': True}
)

if created:
    user.set_password(password)
    user.save()
    print(f"✓ Created demo user: {username} / {password}")
else:
    print(f"✓ Demo user already exists: {username}")

# Призначити роль SUPER_ADMIN
profile, _ = UserProfile.objects.get_or_create(user=user)
profile.role = 'SUPER_ADMIN'
profile.save()
print(f"✓ User {username} set as SUPER_ADMIN")
EOF




