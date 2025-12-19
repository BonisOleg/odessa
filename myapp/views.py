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

# Порожня структура для наповнення через адмінку
# TODO: Підключити реальну модель Company після створення
MOCK_COMPANIES = {}


@login_required
@require_http_methods(["GET"])
def company_list(request):
    """Список компаній"""
    # Отримуємо пошуковий запит
    search_query = request.GET.get('search', '').strip()
    
    # Конвертуємо MOCK_COMPANIES dict в список для шаблону
    companies_list = list(MOCK_COMPANIES.values())
    
    # Фільтрація по пошуковому запиту
    if search_query:
        search_lower = search_query.lower()
        companies_list = [
            c for c in companies_list 
            if (search_lower in c.get('name', '').lower() or
                search_lower in c.get('short_comment', '').lower() or
                search_lower in c.get('city', '').lower() or
                search_lower in c.get('category', '').lower() or
                search_lower in c.get('client_id', '').lower())
        ]
    
    # Сортуємо за датою оновлення (нові зверху)
    companies_list.sort(key=lambda x: x.get('updated_date', ''), reverse=True)
    
    context = {
        'companies': companies_list,
        'total_count': len(companies_list),
        'new_count': 0,  # Буде підраховуватись з реальної БД
        'search_query': search_query
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
    company = MOCK_COMPANIES.get(pk)
    if not company:
        messages.error(request, 'Компанія не знайдена.')
        return redirect('myapp:company_list')
    
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

