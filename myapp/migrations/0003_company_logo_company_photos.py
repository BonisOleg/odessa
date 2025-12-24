# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_initial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, help_text='Логотип компанії', null=True, upload_to='companies/logos/'),
        ),
        migrations.AddField(
            model_name='company',
            name='photos',
            field=models.JSONField(blank=True, default=list, help_text='Список URL фотографій компанії (JSON array)'),
        ),
    ]

