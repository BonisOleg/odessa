"""
Views для CRM Nice.
Початково використовувались MOCK дані, поступово замінюємо на реальну БД.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta

from .forms import CompanyForm, LoginForm, UserProfileForm
from .models import Category, City, Company, CompanyPhone, Status


def is_htmx_request(request: HttpRequest) -> bool:
    """Перевірка чи це HTMX запит"""
    return request.headers.get('HX-Request') == 'true'


# ============================================================================
# Компанії
# ============================================================================

def _process_company_phones(company: Company, phones_data: list, contact_names: list, favorite_phone_index: str | None) -> None:
    """Обробка телефонів компанії при створенні/оновленні."""
    # Видаляємо старі телефони
    CompanyPhone.objects.filter(company=company).delete()
    
    # Створюємо нові телефони
    favorite_index = int(favorite_phone_index) if favorite_phone_index and favorite_phone_index.isdigit() else None
    
    for index, phone in enumerate(phones_data):
        if phone.strip():  # Пропускаємо порожні телефони
            contact_name = contact_names[index] if index < len(contact_names) else ''
            is_favorite = (favorite_index is not None and index == favorite_index)
            
            CompanyPhone.objects.create(
                company=company,
                number=phone.strip(),
                contact_name=contact_name.strip(),
                is_favorite=is_favorite
            )
    
    # Якщо вказано favorite_phone, але він не встановлений, встановлюємо перший телефон як favorite
    if favorite_index is None and phones_data:
        first_phone = CompanyPhone.objects.filter(company=company).first()
        if first_phone:
            first_phone.is_favorite = True
            first_phone.save()


@login_required
@require_http_methods(["GET"])
def company_list(request):
    """Список компаній"""
    # Отримуємо пошуковий запит
    search_query = request.GET.get('search', '').strip()
    
    # Отримуємо параметри фільтрації
    status_filter = request.GET.getlist('status')
    city_filter = request.GET.getlist('city')
    category_filter = request.GET.get('category', '')
    date_updated_filter = request.GET.get('date_updated', '')
    call_date_filter = request.GET.get('call_date', '')
    
    # Отримуємо всі компанії з БД
    companies_queryset = Company.objects.select_related('city', 'category', 'status').prefetch_related('phones').all()
    
    # Фільтрація по пошуковому запиту
    if search_query:
        companies_queryset = companies_queryset.filter(
            Q(name__icontains=search_query) |
            Q(short_comment__icontains=search_query) |
            Q(client_id__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(keywords__icontains=search_query) |
            Q(phones__number__icontains=search_query) |
            Q(phones__contact_name__icontains=search_query)
        ).distinct()
    
    # Фільтрація по статусу
    if status_filter:
        companies_queryset = companies_queryset.filter(status__name__in=status_filter)
    
    # Фільтрація по місту
    if city_filter:
        companies_queryset = companies_queryset.filter(city__name__in=city_filter)
    
    # Фільтрація по розділу
    if category_filter:
        companies_queryset = companies_queryset.filter(category__name=category_filter)
    
    # Фільтрація по даті оновлення
    if date_updated_filter:
        today = timezone.now().date()
        if date_updated_filter == 'today':
            companies_queryset = companies_queryset.filter(updated_at__date=today)
        elif date_updated_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            companies_queryset = companies_queryset.filter(updated_at__date=yesterday)
        elif date_updated_filter == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            companies_queryset = companies_queryset.filter(updated_at__date__gte=week_start)
        elif date_updated_filter == 'this_month':
            companies_queryset = companies_queryset.filter(updated_at__year=today.year, updated_at__month=today.month)
    
    # Фільтрація по даті дзвінка
    if call_date_filter:
        today = timezone.now().date()
        if call_date_filter == 'overdue':
            companies_queryset = companies_queryset.filter(call_date__lt=today)
        elif call_date_filter == 'today':
            companies_queryset = companies_queryset.filter(call_date=today)
        elif call_date_filter == 'this_week':
            week_end = today + timedelta(days=6 - today.weekday())
            companies_queryset = companies_queryset.filter(call_date__gte=today, call_date__lte=week_end)
    
    # Сортуємо за датою оновлення (нові зверху)
    companies_queryset = companies_queryset.order_by('-updated_at')
    
    # Підрахунок нових компаній за останні 30 днів
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_count = Company.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Пагінація
    paginator = Paginator(companies_queryset, 20)  # 20 компаній на сторінку
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'companies': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'new_count': new_count,
        'search_query': search_query
    }
    
    template = 'companies/list_content.html' if is_htmx_request(request) else 'companies/list.html'
    return render(request, template, context)


@login_required
@require_http_methods(["GET", "POST"])
def company_create(request):
    """Форма додавання компанії"""
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        phones_data = request.POST.getlist('phones[]')
        contact_names = request.POST.getlist('contact_names[]')
        favorite_phone_index = request.POST.get('favorite_phone')
        
        if form.is_valid():
            company = form.save()
            _process_company_phones(company, phones_data, contact_names, favorite_phone_index)
            messages.success(request, f'Компанія "{company.name}" успішно створена.')
            if is_htmx_request(request):
                return redirect('myapp:company_detail', pk=company.pk)
            return redirect('myapp:company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    
    template = 'companies/create_content.html' if is_htmx_request(request) else 'companies/create.html'
    context = {
        'form': form,
        'cities': City.objects.all().order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'statuses': Status.objects.all().order_by('name'),
    }
    return render(request, template, context)


@login_required
@require_http_methods(["GET"])
def company_detail(request, pk):
    """Карточка компанії"""
    company = get_object_or_404(
        Company.objects.select_related('city', 'category', 'status').prefetch_related('phones', 'comments'),
        pk=pk
    )
    
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
    company = get_object_or_404(
        Company.objects.select_related('city', 'category', 'status').prefetch_related('phones'),
        pk=pk
    )
    
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES, instance=company)
        phones_data = request.POST.getlist('phones[]')
        contact_names = request.POST.getlist('contact_names[]')
        favorite_phone_index = request.POST.get('favorite_phone')
        
        if form.is_valid():
            company = form.save()
            _process_company_phones(company, phones_data, contact_names, favorite_phone_index)
            messages.success(request, f'Компанія "{company.name}" успішно оновлена.')
            if is_htmx_request(request):
                return redirect('myapp:company_detail', pk=company.pk)
            return redirect('myapp:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    template = 'companies/edit_content.html' if is_htmx_request(request) else 'companies/edit.html'
    context = {
        'form': form,
        'company': company,
        'company_id': pk,
        'cities': City.objects.all().order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'statuses': Status.objects.all().order_by('name'),
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

