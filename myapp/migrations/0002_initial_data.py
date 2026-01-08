# Generated manually for initial data population

from django.db import migrations


def create_initial_data(apps, schema_editor):
    """Створення початкових даних для CRM."""
    Country = apps.get_model('myapp', 'Country')
    City = apps.get_model('myapp', 'City')
    Category = apps.get_model('myapp', 'Category')
    Status = apps.get_model('myapp', 'Status')

    # Countries
    ukraine = Country.objects.create(name='Украина', code='UA', flag_emoji='🇺🇦')
    poland = Country.objects.create(name='Польша', code='PL', flag_emoji='🇵🇱')
    germany = Country.objects.create(name='Германия', code='DE', flag_emoji='🇩🇪')
    czech = Country.objects.create(name='Чехия', code='CZ', flag_emoji='🇨🇿')

    # Cities for Ukraine
    City.objects.create(name='Киев', country=ukraine)
    City.objects.create(name='Харьков', country=ukraine)
    City.objects.create(name='Львов', country=ukraine)
    City.objects.create(name='Одесса', country=ukraine)
    City.objects.create(name='Днепр', country=ukraine)

    # Cities for Poland
    City.objects.create(name='Варшава', country=poland)
    City.objects.create(name='Краков', country=poland)
    City.objects.create(name='Гданьск', country=poland)
    City.objects.create(name='Вроцлав', country=poland)

    # Cities for Germany
    City.objects.create(name='Берлин', country=germany)
    City.objects.create(name='Мюнхен', country=germany)
    City.objects.create(name='Гамбург', country=germany)
    City.objects.create(name='Франкфурт', country=germany)
    City.objects.create(name='Кёльн', country=germany)

    # Cities for Czech
    City.objects.create(name='Прага', country=czech)
    City.objects.create(name='Брно', country=czech)
    City.objects.create(name='Острава', country=czech)

    # Categories
    Category.objects.create(
        name='IT-услуги',
        badge_color_bg='#3B82F6',
        badge_color_fg='#FFFFFF',
        badge_class='badge--custom-blue'
    )
    Category.objects.create(
        name='Ресторан',
        badge_color_bg='#10B981',
        badge_color_fg='#FFFFFF',
        badge_class='badge--success'
    )
    Category.objects.create(
        name='Образование',
        badge_color_bg='#F59E0B',
        badge_color_fg='#FFFFFF',
        badge_class='badge--warning'
    )
    Category.objects.create(
        name='Недвижимость',
        badge_color_bg='#8B5CF6',
        badge_color_fg='#FFFFFF',
        badge_class='badge--custom-purple'
    )

    # Statuses
    Status.objects.create(
        name='Новый',
        is_default=True,
        badge_class='badge--secondary'
    )
    Status.objects.create(
        name='В работе',
        is_default=False,
        badge_class='badge--primary'
    )
    Status.objects.create(
        name='Закрыто',
        is_default=False,
        badge_class='badge--success'
    )


def reverse_initial_data(apps, schema_editor):
    """Видалення початкових даних (для rollback)."""
    Country = apps.get_model('myapp', 'Country')
    Category = apps.get_model('myapp', 'Category')
    Status = apps.get_model('myapp', 'Status')

    Country.objects.filter(code__in=['UA', 'PL', 'DE', 'CZ']).delete()
    Category.objects.filter(name__in=['IT-услуги', 'Ресторан', 'Образование', 'Недвижимость']).delete()
    Status.objects.filter(name__in=['Новый', 'В работе', 'Закрыто']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_initial_data),
    ]



