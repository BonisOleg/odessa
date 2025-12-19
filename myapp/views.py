"""
Views для CRM Nice.
Початково використовувались MOCK дані, поступово замінюємо на реальну БД.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, UserProfileForm


def is_htmx_request(request: HttpRequest) -> bool:
    """Перевірка чи це HTMX запит"""
    return request.headers.get('HX-Request') == 'true'


# ============================================================================
# Компанії
# ============================================================================

# Mock дані для компаній
MOCK_COMPANIES = {
    1: {
        'id': 1,
        'client_id': '#00123',
        'name': 'IT Solutions Ltd',
        'logo': 'https://via.placeholder.com/60',
        'status': 'В работе',
        'status_badge': 'badge--success',
        'phones': [
            {'number': '+380991234567', 'name': 'Иван Петров', 'favorite': True},
            {'number': '+380501234567', 'name': 'Мария Сидорова', 'favorite': False}
        ],
        'telegram': '@itsolutions',
        'website': 'https://itsolutions.com',
        'instagram': '@itsolutions',
        'city': 'Киев',
        'category': 'IT-услуги',
        'category_badge': 'badge--custom-blue',
        'keywords': ['CRM', 'Django', 'HTMX', 'Разработка'],
        'short_comment': 'Отправлено коммерческое предложение по разработке CRM-системы',
        'full_description': 'Компания занимается разработкой CRM-систем и веб-приложений на Django. Основные клиенты - средний и крупный бизнес. Работают на рынке более 5 лет. В штате 15 разработчиков.',
        'call_date': '2025-11-28',
        'call_date_display': '28.11.2025',
        'created_date': '15.11.2025 10:30',
        'updated_date': '24.11.2025 10:30',
        'photos': [
            'https://via.placeholder.com/400x300',
            'https://via.placeholder.com/400x300',
            'https://via.placeholder.com/400x300'
        ],
        'comments': [
            {'author': 'Иван Петров', 'date': '24.11.2025 10:30', 'text': 'Созвонились с директором, договорились о встрече на следующей неделе. Обсудим детали проекта и бюджет.'},
            {'author': 'Мария Сидорова', 'date': '20.11.2025 14:15', 'text': 'Отправила коммерческое предложение на email. Жду обратной связи в течение 3 дней.'},
            {'author': 'Иван Петров', 'date': '18.11.2025 09:00', 'text': 'Первый контакт. Компания заинтересована в разработке CRM. Запросили информацию о ценах и сроках.'},
            {'author': 'Петр Иванов', 'date': '15.11.2025 16:20', 'text': 'Дополнительная информация о проекте была отправлена на почту.'},
            {'author': 'Анна Смирнова', 'date': '12.11.2025 11:00', 'text': 'Первичный звонок. Клиент заинтересован в сотрудничестве.'}
        ]
    },
    2: {
        'id': 2,
        'client_id': '#00124',
        'name': 'Restaurant Pro',
        'logo': 'https://via.placeholder.com/60',
        'status': 'Позже',
        'status_badge': 'badge--warning',
        'phones': [
            {'number': '+380501234567', 'name': 'Мария Сидорова', 'favorite': True}
        ],
        'telegram': '@restaurantpro',
        'website': None,
        'instagram': None,
        'city': 'Львов',
        'category': 'Ресторан',
        'category_badge': 'badge--custom-red',
        'keywords': ['Ресторан', 'Кейтеринг', 'Банкеты'],
        'short_comment': 'Ждем обратной связи',
        'full_description': 'Сеть ресторанов премиум-класса. Специализируются на европейской кухне. Имеют 5 заведений в разных городах.',
        'call_date': '2025-11-20',
        'call_date_display': '20.11.2025',
        'created_date': '10.11.2025 14:00',
        'updated_date': '23.11.2025 16:45',
        'photos': [],
        'comments': [
            {'author': 'Мария Сидорова', 'date': '23.11.2025 16:45', 'text': 'Отправили предложение по кейтерингу для корпоративных мероприятий.'},
            {'author': 'Иван Петров', 'date': '20.11.2025 11:30', 'text': 'Первичный контакт. Заинтересованы в автоматизации заказов.'}
        ]
    },
    3: {
        'id': 3,
        'client_id': '#00125',
        'name': 'EduTech Solutions',
        'logo': 'https://via.placeholder.com/60',
        'status': 'Горячий',
        'status_badge': 'badge--info',
        'phones': [
            {'number': '+380671234567', 'name': 'Петр Иванов', 'favorite': True}
        ],
        'telegram': '@edutech',
        'website': 'https://edutech.com',
        'instagram': None,
        'city': 'Харьков',
        'category': 'Образование',
        'category_badge': 'badge--custom-green',
        'keywords': ['Образование', 'Онлайн-курсы', 'E-learning'],
        'short_comment': 'Очень заинтересованы',
        'full_description': 'Платформа для онлайн-обучения. Разрабатывают курсы по программированию и дизайну. Более 10,000 активных студентов.',
        'call_date': '2025-11-30',
        'call_date_display': '30.11.2025',
        'created_date': '18.11.2025 09:15',
        'updated_date': '25.11.2025 14:20',
        'photos': [
            'https://via.placeholder.com/400x300'
        ],
        'comments': [
            {'author': 'Петр Иванов', 'date': '25.11.2025 14:20', 'text': 'Очень заинтересованы в CRM для управления студентами и курсами.'},
            {'author': 'Анна Коваль', 'date': '22.11.2025 10:00', 'text': 'Отправили презентацию платформы.'}
        ]
    },
    4: {
        'id': 4,
        'client_id': '#00126',
        'name': 'Fitness Club Premium',
        'logo': 'https://via.placeholder.com/60',
        'status': 'Хороший',
        'status_badge': 'badge--success',
        'phones': [
            {'number': '+380931234567', 'name': 'Ольга Шевченко', 'favorite': True},
            {'number': '+380631234567', 'name': 'Андрей Коваль', 'favorite': False}
        ],
        'telegram': '@fitnesspremium',
        'website': 'https://fitnesspremium.com',
        'instagram': '@fitnesspremium',
        'city': 'Одесса',
        'category': 'Фитнес',
        'category_badge': 'badge--custom-purple',
        'keywords': ['Фитнес', 'Тренажерный зал', 'Йога'],
        'short_comment': 'Планируют открыть новый филиал',
        'full_description': 'Сеть фитнес-клубов премиум-класса. 3 зала в разных районах города. Более 5000 активных членов.',
        'call_date': '2025-12-05',
        'call_date_display': '05.12.2025',
        'created_date': '20.11.2025 12:00',
        'updated_date': '26.11.2025 15:30',
        'photos': [],
        'comments': [
            {'author': 'Ольга Шевченко', 'date': '26.11.2025 15:30', 'text': 'Планируют открыть новый филиал в следующем году. Нужна CRM для управления клубами.'}
        ]
    },
    5: {
        'id': 5,
        'client_id': '#00127',
        'name': 'Beauty Salon Luxe',
        'logo': 'https://via.placeholder.com/60',
        'status': 'Теплый',
        'status_badge': 'badge--secondary',
        'phones': [
            {'number': '+380971234567', 'name': 'Елена Петрова', 'favorite': True}
        ],
        'telegram': None,
        'website': None,
        'instagram': '@beautyluxe',
        'city': 'Днепр',
        'category': 'Красота',
        'category_badge': 'badge--custom-pink',
        'keywords': ['Салон красоты', 'Парикмахерская', 'Маникюр'],
        'short_comment': 'Интересуются системой записи',
        'full_description': 'Салон красоты премиум-класса. Предоставляют услуги парикмахера, маникюра, педикюра. Работают более 8 лет.',
        'call_date': '2025-11-25',
        'call_date_display': '25.11.2025',
        'created_date': '15.11.2025 11:00',
        'updated_date': '27.11.2025 10:15',
        'photos': [],
        'comments': [
            {'author': 'Елена Петрова', 'date': '27.11.2025 10:15', 'text': 'Интересуются системой онлайн-записи для клиентов.'},
            {'author': 'Мария Сидорова', 'date': '25.11.2025 09:00', 'text': 'Первый контакт. Нужна автоматизация записи клиентов.'}
        ]
    }
}


@login_required
@require_http_methods(["GET"])
def company_list(request):
    """Список компаній"""
    # Конвертуємо MOCK_COMPANIES dict в список для шаблону
    companies_list = list(MOCK_COMPANIES.values())
    
    # Сортуємо за датою оновлення (нові зверху)
    companies_list.sort(key=lambda x: x.get('updated_date', ''), reverse=True)
    
    context = {
        'companies': companies_list,
        'total_count': len(companies_list),
        'new_count': 5  # Mock значення для "Новых за 30 дней"
    }
    
    template = 'companies/list_content.html' if is_htmx_request(request) else 'companies/list.html'
    return render(request, template, context)


@login_required
@require_http_methods(["GET", "POST"])
def company_create(request):
    """Форма додавання компанії"""
    template = 'companies/create_content.html' if is_htmx_request(request) else 'companies/create.html'
    return render(request, template)


@login_required
@require_http_methods(["GET"])
def company_detail(request, pk):
    """Карточка компанії"""
    company = MOCK_COMPANIES.get(pk, MOCK_COMPANIES[1])
    context = {
        'company': company,
        'company_id': pk
    }
    if is_htmx_request(request):
        return render(request, 'companies/detail_content.html', context)
    return render(request, 'companies/detail.html', context)


@login_required
@require_http_methods(["GET"])
def company_delete(request, pk):
    """Модальне вікно підтвердження видалення компанії"""
    context = {
        'company_id': pk,
        'company_name': 'IT Solutions Ltd'
    }
    return render(request, 'companies/delete_modal.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def company_edit(request, pk):
    """Форма редагування компанії"""
    template = 'companies/edit_content.html' if is_htmx_request(request) else 'companies/edit.html'
    context = {
        'company_id': pk
    }
    return render(request, template, context)


# ============================================================================
# Налаштування
# ============================================================================

@login_required
@require_http_methods(["GET"])
def settings_dashboard(request):
    """Головна сторінка налаштувань"""
    template = 'settings/dashboard_content.html' if is_htmx_request(request) else 'settings/dashboard.html'
    return render(request, template)


@login_required
@require_http_methods(["GET"])
def settings_countries(request):
    """Управління країнами"""
    template = 'settings/countries_content.html' if is_htmx_request(request) else 'settings/countries.html'
    return render(request, template)


@login_required
@require_http_methods(["GET"])
def settings_cities(request):
    """Управління містами"""
    template = 'settings/cities_content.html' if is_htmx_request(request) else 'settings/cities.html'
    return render(request, template)


@login_required
@require_http_methods(["GET"])
def settings_categories(request):
    """Управління розділами"""
    template = 'settings/categories_content.html' if is_htmx_request(request) else 'settings/categories.html'
    return render(request, template)


@login_required
@require_http_methods(["GET"])
def settings_statuses(request):
    """Управління статусами"""
    template = 'settings/statuses_content.html' if is_htmx_request(request) else 'settings/statuses.html'
    return render(request, template)


@login_required
@require_http_methods(["GET"])
def settings_users(request):
    """Управління користувачами"""
    template = 'settings/users_content.html' if is_htmx_request(request) else 'settings/users.html'
    return render(request, template)


# ============================================================================
# Модальні вікна для налаштувань
# ============================================================================

@login_required
@require_http_methods(["GET"])
def settings_country_add(request):
    """Модальне вікно додавання країни"""
    return render(request, 'settings/modals/country_add.html')


@login_required
@require_http_methods(["GET"])
def settings_country_edit(request, pk):
    """Модальне вікно редагування країни"""
    context = {'country_id': pk}
    return render(request, 'settings/modals/country_edit.html', context)


@login_required
@require_http_methods(["GET"])
def settings_country_delete(request, pk):
    """Модальне вікно підтвердження видалення країни"""
    context = {'country_id': pk, 'country_name': 'Украина'}
    return render(request, 'settings/modals/country_delete.html', context)


@login_required
@require_http_methods(["GET"])
def settings_city_add(request):
    """Модальне вікно додавання міста"""
    return render(request, 'settings/modals/city_add.html')


@login_required
@require_http_methods(["GET"])
def settings_city_edit(request, pk):
    """Модальне вікно редагування міста"""
    context = {'city_id': pk}
    return render(request, 'settings/modals/city_edit.html', context)


@login_required
@require_http_methods(["GET"])
def settings_city_delete(request, pk):
    """Модальне вікно підтвердження видалення міста"""
    context = {'city_id': pk, 'city_name': 'Киев'}
    return render(request, 'settings/modals/city_delete.html', context)


@login_required
@require_http_methods(["GET"])
def settings_category_add(request):
    """Модальне вікно додавання розділу"""
    return render(request, 'settings/modals/category_add.html')


@login_required
@require_http_methods(["GET"])
def settings_category_edit(request, pk):
    """Модальне вікно редагування розділу"""
    context = {'category_id': pk}
    return render(request, 'settings/modals/category_edit.html', context)


@login_required
@require_http_methods(["GET"])
def settings_category_delete(request, pk):
    """Модальне вікно підтвердження видалення розділу"""
    context = {'category_id': pk, 'category_name': 'IT-услуги'}
    return render(request, 'settings/modals/category_delete.html', context)


@login_required
@require_http_methods(["GET"])
def settings_status_add(request):
    """Модальне вікно додавання статусу"""
    return render(request, 'settings/modals/status_add.html')


@login_required
@require_http_methods(["GET"])
def settings_status_edit(request, pk):
    """Модальне вікно редагування статусу"""
    context = {'status_id': pk}
    return render(request, 'settings/modals/status_edit.html', context)


@login_required
@require_http_methods(["GET"])
def settings_status_delete(request, pk):
    """Модальне вікно підтвердження видалення статусу"""
    context = {'status_id': pk, 'status_name': 'В работе'}
    return render(request, 'settings/modals/status_delete.html', context)


@login_required
@require_http_methods(["GET"])
def settings_user_add(request):
    """Модальне вікно додавання користувача"""
    return render(request, 'settings/modals/user_add.html')


@login_required
@require_http_methods(["GET"])
def settings_user_edit(request, pk):
    """Модальне вікно редагування користувача"""
    context = {'user_id': pk}
    return render(request, 'settings/modals/user_edit.html', context)


@login_required
@require_http_methods(["GET"])
def settings_user_delete(request, pk):
    """Модальне вікно підтвердження видалення користувача"""
    context = {'user_id': pk, 'user_name': 'Мария Сидорова'}
    return render(request, 'settings/modals/user_delete.html', context)


@login_required
@require_http_methods(["GET"])
def profile_edit(request):
    """Модальне вікно редагування профілю + обробка POST."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено.")
            return redirect("myapp:profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "accounts/profile_edit_modal.html", {"form": form})


# ============================================================================
# Заглушки для інших розділів
# ============================================================================

@require_http_methods(["GET"])
def stub_page(request):
    """Заглушка для розділів в розробці"""
    template = 'stubs/in_development_content.html' if is_htmx_request(request) else 'stubs/in_development.html'
    return render(request, template)


# ============================================================================
# Accounts
# ============================================================================

@require_http_methods(["GET", "POST"])
def login_page(request):
    """Сторінка логіну з обробкою POST."""
    if request.user.is_authenticated:
        return redirect("myapp:company_list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            return redirect("myapp:company_list")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
@require_http_methods(["GET"])
def profile_page(request):
    """Профіль користувача"""
    template = 'accounts/profile_content.html' if is_htmx_request(request) else 'accounts/profile.html'
    return render(request, template)


@login_required
@require_http_methods(["POST", "GET"])
def logout_view(request):
    """Вихід користувача з системи."""
    logout(request)
    return redirect("myapp:login")

