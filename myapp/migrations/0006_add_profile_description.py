# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_create_user_profiles_for_existing_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_description',
            field=models.TextField(blank=True, default='', help_text='Про користувача (телефон, відділ тощо)', max_length=500),
        ),
    ]
