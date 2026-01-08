# Generated manually

from django.db import migrations


def create_user_profiles(apps, schema_editor):
    """Створює UserProfile для всіх існуючих користувачів."""
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('myapp', 'UserProfile')
    
    for user in User.objects.all():
        UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'MANAGER'}
        )


def reverse_create_user_profiles(apps, schema_editor):
    """Зворотна операція - видаляє UserProfile (не використовується, але потрібна для міграції)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_userprofile_userfavoritecompany_companyaddress'),
    ]

    operations = [
        migrations.RunPython(create_user_profiles, reverse_code=reverse_create_user_profiles),
    ]



