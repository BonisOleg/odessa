# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0003_company_logo_company_photos'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('SUPER_ADMIN', 'Супер адмін'), ('OBSERVER', 'Спостерігач'), ('MANAGER', 'Менеджер')], default='MANAGER', help_text='Роль користувача в системі', max_length=20)),
                ('avatar', models.ImageField(blank=True, help_text='Аватар користувача', null=True, upload_to='avatars/')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('language', models.CharField(default='ru', help_text='Мова інтерфейсу (ru, en, uk)', max_length=10)),
                ('country', models.ForeignKey(blank=True, help_text='Призначена країна для користувача', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_profiles', to='myapp.country')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'ordering': ('user__username',),
            },
        ),
        migrations.CreateModel(
            name='UserFavoriteCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='myapp.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_companies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Favorite Company',
                'verbose_name_plural': 'User Favorite Companies',
                'ordering': ('-created_at',),
                'unique_together': {('user', 'company')},
            },
        ),
        migrations.CreateModel(
            name='CompanyAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=500)),
                ('is_favorite', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='myapp.company')),
            ],
            options={
                'verbose_name': 'Company Address',
                'verbose_name_plural': 'Company Addresses',
            },
        ),
    ]

