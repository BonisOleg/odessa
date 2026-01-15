# Generated manually

from django.db import migrations


def set_first_superadmin(apps, schema_editor):
    """Призначає першого користувача (або Django superuser) як SUPER_ADMIN."""
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('myapp', 'UserProfile')
    
    # Спробувати знайти Django superuser
    superuser = User.objects.filter(is_superuser=True).first()
    
    if superuser:
        # Якщо є Django superuser, зробити його SUPER_ADMIN
        profile, created = UserProfile.objects.get_or_create(user=superuser)
        profile.role = 'SUPER_ADMIN'
        profile.save()
        print(f"✓ Користувач {superuser.username} призначений SUPER_ADMIN")
    else:
        # Якщо немає superuser, взяти першого користувача
        first_user = User.objects.order_by('id').first()
        if first_user:
            profile, created = UserProfile.objects.get_or_create(user=first_user)
            profile.role = 'SUPER_ADMIN'
            profile.save()
            print(f"✓ Користувач {first_user.username} призначений SUPER_ADMIN")


def reverse_set_first_superadmin(apps, schema_editor):
    """Зворотна операція."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_companyaddress_options_company_on_site_url_and_more'),
    ]

    operations = [
        migrations.RunPython(set_first_superadmin, reverse_set_first_superadmin),
    ]
