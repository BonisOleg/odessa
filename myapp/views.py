"""
Views для CRM Nice.
Початково використовувались MOCK дані, поступово замінюємо на реальну БД.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta

from .forms import CategoryForm, CityForm, CompanyForm, CountryForm, LoginForm, StatusForm, UserProfileForm
from .models import Category, City, Company, CompanyPhone, Country, Status


def is_htmx_request(request: HttpRequest) -> bool:
    """Перевірка чи це HTMX запит"""
    return request.headers.get('HX-Request') == 'true'


# ============================================================================
# Компанії
# ============================================================================

def _process_company_phones(company: Company, phones_data: list, contact_names: list, favorite_phone_index: str | None) -> None:
    """Обробка телефонів компанії при створенні/оновленні."""
    # Фільтруємо порожні телефони
    valid_phones = [phone.strip() for phone in phones_data if phone.strip()]
    
    # Валідація: має бути хоча б один телефон
    if not valid_phones:
        raise ValueError("Компанія повинна мати хоча б один телефон")
    
    # Видаляємо старі телефони
    CompanyPhone.objects.filter(company=company).delete()
    
    # Створюємо нові телефони
    favorite_index = int(favorite_phone_index) if favorite_phone_index and favorite_phone_index.isdigit() else None
    
    for index, phone in enumerate(valid_phones):
        contact_name = contact_names[index] if index < len(contact_names) else ''
        is_favorite = (favorite_index is not None and index == favorite_index)
        
        CompanyPhone.objects.create(
            company=company,
            number=phone.strip(),
            contact_name=contact_name.strip(),
            is_favorite=is_favorite
        )
    
    # Якщо вказано favorite_phone, але він не встановлений, встановлюємо перший телефон як favorite
    if favorite_index is None and valid_phones:
        first_phone = CompanyPhone.objects.filter(company=company).first()
        if first_phone:
            first_phone.is_favorite = True
            first_phone.save()


def _process_company_photos(company: Company, photos_files) -> None:
    """Обробка фотографій компанії при створенні/оновленні."""
    if not photos_files:
        return
    
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import os
    from django.utils import timezone
    
    # Валідація типів файлів
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    photos_list = company.photos if company.photos else []
    
    for photo_file in photos_files:
        # Валідація розміру файлу
        if photo_file.size > MAX_FILE_SIZE:
            raise ValueError(f'Файл "{photo_file.name}" занадто великий. Максимальний розмір: 10 MB')
        
        # Валідація розширення
        file_ext = os.path.splitext(photo_file.name)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f'Файл "{photo_file.name}" має недозволений формат. Дозволені: {", ".join(ALLOWED_EXTENSIONS)}')
        
        # Генеруємо унікальне ім'я файлу
        timestamp = int(timezone.now().timestamp())
        file_name = f"companies/photos/{company.id}_{timestamp}_{len(photos_list)}{file_ext}"
        
        # Читаємо вміст файлу
        photo_file.seek(0)  # Повертаємося на початок файлу
        file_content = photo_file.read()
        
        # Зберігаємо файл
        saved_path = default_storage.save(file_name, ContentFile(file_content))
        
        # Додаємо URL до списку
        photos_list.append(default_storage.url(saved_path))
    
    company.photos = photos_list
    company.save()


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
    
    # Отримуємо унікальні значення для фільтрів
    all_statuses = Status.objects.all().order_by('name')
    all_cities = City.objects.all().order_by('name')
    all_categories = Category.objects.all().order_by('name')
    
    context = {
        'companies': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'new_count': new_count,
        'search_query': search_query,
        'all_statuses': all_statuses,
        'all_cities': all_cities,
        'all_categories': all_categories,
        'selected_statuses': status_filter,
        'selected_cities': city_filter,
        'selected_category': category_filter,
        'selected_date_updated': date_updated_filter,
        'selected_call_date': call_date_filter,
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
            try:
                company = form.save()
                _process_company_phones(company, phones_data, contact_names, favorite_phone_index)
                # Обробка photos
                if 'photos' in request.FILES:
                    _process_company_photos(company, request.FILES.getlist('photos'))
                messages.success(request, f'Компанія "{company.name}" успішно створена.')
                if is_htmx_request(request):
                    return redirect('myapp:company_detail', pk=company.pk)
                return redirect('myapp:company_detail', pk=company.pk)
            except ValueError as e:
                messages.error(request, str(e))
                # Повертаємо форму з помилкою
                template = 'companies/create_content.html' if is_htmx_request(request) else 'companies/create.html'
                context = {
                    'form': form,
                    'cities': City.objects.all().order_by('name'),
                    'categories': Category.objects.all().order_by('name'),
                    'statuses': Status.objects.all().order_by('name'),
                }
                return render(request, template, context, status=400)
        else:
            # Форма невалідна - показуємо помилки
            messages.error(request, 'Будь ласка, виправте помилки в формі.')
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
@require_http_methods(["GET", "POST"])
def company_delete(request, pk):
    """Модальне вікно підтвердження видалення компанії та видалення компанії"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == "POST":
        company_name = company.name
        company.delete()
        messages.success(request, f'Компанія "{company_name}" успішно видалена.')
        if is_htmx_request(request):
            return redirect('myapp:company_list')
        return redirect('myapp:company_list')
    
    context = {
        'company_id': pk,
        'company': company,
        'company_name': company.name
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
            try:
                company = form.save()
                _process_company_phones(company, phones_data, contact_names, favorite_phone_index)
                # Обробка photos
                if 'photos' in request.FILES:
                    _process_company_photos(company, request.FILES.getlist('photos'))
                messages.success(request, f'Компанія "{company.name}" успішно оновлена.')
                if is_htmx_request(request):
                    return redirect('myapp:company_detail', pk=company.pk)
                return redirect('myapp:company_detail', pk=company.pk)
            except ValueError as e:
                messages.error(request, str(e))
                # Повертаємо форму з помилкою
                template = 'companies/edit_content.html' if is_htmx_request(request) else 'companies/edit.html'
                context = {
                    'form': form,
                    'company': company,
                    'company_id': pk,
                    'cities': City.objects.all().order_by('name'),
                    'categories': Category.objects.all().order_by('name'),
                    'statuses': Status.objects.all().order_by('name'),
                }
                return render(request, template, context, status=400)
        else:
            # Форма невалідна - показуємо помилки
            messages.error(request, 'Будь ласка, виправте помилки в формі.')
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


@login_required
@require_http_methods(["POST"])
def company_update_short_comment(request, pk):
    """AJAX endpoint для збереження короткого коментаря"""
    company = get_object_or_404(Company, pk=pk)
    short_comment = request.POST.get('short_comment', '').strip()
    
    if len(short_comment) > 500:
        return HttpResponse('Короткий коментар не може перевищувати 500 символів', status=400)
    
    company.short_comment = short_comment
    company.save()
    
    return HttpResponse('OK', status=200)


@login_required
@require_http_methods(["POST"])
def company_update_call_date(request, pk):
    """AJAX endpoint для збереження дати дзвінка"""
    company = get_object_or_404(Company, pk=pk)
    call_date_str = request.POST.get('call_date', '').strip()
    
    if call_date_str:
        try:
            from datetime import datetime
            call_date = datetime.strptime(call_date_str, '%Y-%m-%d').date()
            company.call_date = call_date
        except ValueError:
            return HttpResponse('Невірний формат дати', status=400)
    else:
        company.call_date = None
    
    company.save()
    
    return HttpResponse('OK', status=200)


@login_required
@require_http_methods(["POST"])
def company_comment_add(request, pk):
    """AJAX endpoint для додавання коментаря"""
    company = get_object_or_404(Company, pk=pk)
    comment_text = request.POST.get('comment', '').strip()
    
    if not comment_text:
        return HttpResponse('Коментар не може бути порожнім', status=400)
    
    author_name = request.user.get_full_name() or request.user.username
    
    CompanyComment.objects.create(
        company=company,
        author_name=author_name,
        text=comment_text
    )
    
    if is_htmx_request(request):
        return redirect('myapp:company_detail', pk=company.pk)
    return redirect('myapp:company_detail', pk=company.pk)


@login_required
@require_http_methods(["POST"])
def company_comment_delete(request, pk, comment_id):
    """AJAX endpoint для видалення коментаря"""
    company = get_object_or_404(Company, pk=pk)
    comment = get_object_or_404(CompanyComment, pk=comment_id, company=company)
    
    comment.delete()
    
    if is_htmx_request(request):
        return redirect('myapp:company_detail', pk=company.pk)
    return redirect('myapp:company_detail', pk=company.pk)


@login_required
@require_http_methods(["POST"])
def company_delete_logo(request, pk):
    """AJAX endpoint для видалення логотипу"""
    company = get_object_or_404(Company, pk=pk)
    
    if company.logo:
        company.logo.delete()
        company.logo = None
        company.save()
    
    if is_htmx_request(request):
        return redirect('myapp:company_detail', pk=company.pk)
    return redirect('myapp:company_detail', pk=company.pk)


@login_required
@require_http_methods(["POST"])
def company_delete_photo(request, pk):
    """AJAX endpoint для видалення фото"""
    company = get_object_or_404(Company, pk=pk)
    photo_url = request.POST.get('photo_url', '').strip()
    
    if photo_url and company.photos:
        photos_list = list(company.photos)
        if photo_url in photos_list:
            photos_list.remove(photo_url)
            company.photos = photos_list
            company.save()
            
            # Видалити файл з файлової системи
            try:
                from django.core.files.storage import default_storage
                from django.conf import settings
                import os
                # Отримуємо шлях файлу з URL
                if photo_url.startswith(settings.MEDIA_URL):
                    file_path = photo_url.replace(settings.MEDIA_URL, '')
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
            except Exception:
                pass  # Ігноруємо помилки видалення файлу
    
    if is_htmx_request(request):
        return redirect('myapp:company_detail', pk=company.pk)
    return redirect('myapp:company_detail', pk=company.pk)


@login_required
@require_http_methods(["GET"])
def company_export(request, pk):
    """Експорт компанії в CSV формат"""
    import csv
    from django.http import HttpResponse
    
    company = get_object_or_404(
        Company.objects.select_related('city', 'category', 'status').prefetch_related('phones', 'comments'),
        pk=pk
    )
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="company_{company.client_id}_{company.name}.csv"'
    
    writer = csv.writer(response)
    
    # Заголовки
    writer.writerow(['Поле', 'Значення'])
    
    # Основна інформація
    writer.writerow(['ID', company.client_id])
    writer.writerow(['Назва', company.name])
    writer.writerow(['Місто', company.city.name if company.city else ''])
    writer.writerow(['Розділ', company.category.name if company.category else ''])
    writer.writerow(['Статус', company.status.name if company.status else ''])
    writer.writerow(['Telegram', company.telegram])
    writer.writerow(['Сайт', company.website])
    writer.writerow(['Instagram', company.instagram])
    writer.writerow(['Короткий коментар', company.short_comment])
    writer.writerow(['Повний опис', company.full_description])
    writer.writerow(['Ключові слова', company.keywords])
    writer.writerow(['Дата дзвінка', company.call_date.strftime('%d.%m.%Y') if company.call_date else ''])
    writer.writerow(['Дата створення', company.created_at.strftime('%d.%m.%Y %H:%M')])
    writer.writerow(['Дата оновлення', company.updated_at.strftime('%d.%m.%Y %H:%M')])
    
    # Телефони
    writer.writerow([])
    writer.writerow(['Телефони'])
    for phone in company.phones.all():
        favorite = '⭐' if phone.is_favorite else ''
        writer.writerow([f'{favorite} {phone.number}', phone.contact_name])
    
    # Коментарі
    writer.writerow([])
    writer.writerow(['Коментарі'])
    for comment in company.comments.all():
        writer.writerow([f'{comment.created_at.strftime("%d.%m.%Y %H:%M")} - {comment.author_name}', comment.text])
    
    return response


@login_required
@require_http_methods(["GET"])
def company_check_duplicates(request):
    """AJAX endpoint для перевірки дублікатів"""
    from django.http import JsonResponse
    
    phone = request.GET.get('phone', '').strip()
    website = request.GET.get('website', '').strip()
    instagram = request.GET.get('instagram', '').strip()
    telegram = request.GET.get('telegram', '').strip()
    exclude_id = request.GET.get('exclude_id', '')
    
    duplicates = {}
    
    # Перевірка телефону
    if phone:
        query = CompanyPhone.objects.filter(number=phone)
        if exclude_id:
            query = query.exclude(company_id=exclude_id)
        if query.exists():
            duplicates['phone'] = {
                'exists': True,
                'company': query.first().company.name
            }
        else:
            duplicates['phone'] = {'exists': False}
    
    # Перевірка website
    if website:
        query = Company.objects.filter(website=website)
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        if query.exists():
            duplicates['website'] = {
                'exists': True,
                'company': query.first().name
            }
        else:
            duplicates['website'] = {'exists': False}
    
    # Перевірка instagram
    if instagram:
        query = Company.objects.filter(instagram=instagram)
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        if query.exists():
            duplicates['instagram'] = {
                'exists': True,
                'company': query.first().name
            }
        else:
            duplicates['instagram'] = {'exists': False}
    
    # Перевірка telegram
    if telegram:
        query = Company.objects.filter(telegram=telegram)
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        if query.exists():
            duplicates['telegram'] = {
                'exists': True,
                'company': query.first().name
            }
        else:
            duplicates['telegram'] = {'exists': False}
    
    return JsonResponse(duplicates)


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
@require_http_methods(["GET", "POST"])
def settings_countries(request):
    """Управління країнами"""
    countries = Country.objects.annotate(
        cities_count=Count('cities', distinct=True)
    ).order_by('name')
    
    template = 'settings/countries_content.html' if is_htmx_request(request) else 'settings/countries.html'
    context = {'countries': countries}
    return render(request, template, context)


@login_required
@require_http_methods(["GET", "POST"])
def settings_cities(request):
    """Управління містами"""
    country_filter = request.GET.get('country', '')
    cities_queryset = City.objects.select_related('country').annotate(
        companies_count=Count('companies', distinct=True)
    ).order_by('name')
    
    if country_filter:
        cities_queryset = cities_queryset.filter(country_id=country_filter)
    
    countries = Country.objects.all().order_by('name')
    
    template = 'settings/cities_content.html' if is_htmx_request(request) else 'settings/cities.html'
    context = {
        'cities': cities_queryset,
        'countries': countries,
        'selected_country': country_filter,
    }
    return render(request, template, context)


@login_required
@require_http_methods(["GET", "POST"])
def settings_categories(request):
    """Управління розділами"""
    categories = Category.objects.annotate(
        companies_count=Count('companies', distinct=True)
    ).order_by('name')
    
    template = 'settings/categories_content.html' if is_htmx_request(request) else 'settings/categories.html'
    context = {'categories': categories}
    return render(request, template, context)


@login_required
@require_http_methods(["GET", "POST"])
def settings_statuses(request):
    """Управління статусами"""
    statuses = Status.objects.annotate(
        companies_count=Count('companies', distinct=True)
    ).order_by('-is_default', 'name')
    
    template = 'settings/statuses_content.html' if is_htmx_request(request) else 'settings/statuses.html'
    context = {'statuses': statuses}
    return render(request, template, context)


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
    form = CountryForm()
    return render(request, 'settings/modals/country_add.html', {'form': form})


@login_required
@require_http_methods(["GET"])
def settings_country_edit(request, pk):
    """Модальне вікно редагування країни"""
    country = get_object_or_404(Country, pk=pk)
    form = CountryForm(instance=country)
    return render(request, 'settings/modals/country_edit.html', {'form': form, 'country': country})


@login_required
@require_http_methods(["GET"])
def settings_country_delete(request, pk):
    """Модальне вікно підтвердження видалення країни"""
    country = get_object_or_404(Country, pk=pk)
    cities_count = country.cities.count()
    return render(request, 'settings/modals/country_delete.html', {'country': country, 'cities_count': cities_count})


@login_required
@require_http_methods(["POST"])
def country_create(request):
    """Створення країни через HTMX"""
    form = CountryForm(request.POST)
    if form.is_valid():
        country = form.save()
        messages.success(request, f'Країна "{country.name}" успішно додана.')
        if is_htmx_request(request):
            return redirect('myapp:settings_countries')
        return redirect('myapp:settings_countries')
    else:
        messages.error(request, 'Помилка валідації форми.')
        return render(request, 'settings/modals/country_add.html', {'form': form}, status=400)


@login_required
@require_http_methods(["POST"])
def country_update(request, pk):
    """Оновлення країни через HTMX"""
    country = get_object_or_404(Country, pk=pk)
    form = CountryForm(request.POST, instance=country)
    if form.is_valid():
        country = form.save()
        messages.success(request, f'Країна "{country.name}" успішно оновлена.')
        if is_htmx_request(request):
            return redirect('myapp:settings_countries')
        return redirect('myapp:settings_countries')
    else:
        messages.error(request, 'Помилка валідації форми.')
        return render(request, 'settings/modals/country_edit.html', {'form': form, 'country': country}, status=400)


@login_required
@require_http_methods(["POST"])
def country_delete(request, pk):
    """Видалення країни через HTMX"""
    country = get_object_or_404(Country, pk=pk)
    cities_count = country.cities.count()
    if cities_count > 0:
        messages.error(request, f'Неможливо видалити країну "{country.name}", оскільки до неї прив\'язано {cities_count} міст.')
        if is_htmx_request(request):
            return redirect('myapp:settings_countries')
        return redirect('myapp:settings_countries')
    
    country_name = country.name
    country.delete()
    messages.success(request, f'Країна "{country_name}" успішно видалена.')
    if is_htmx_request(request):
        return redirect('myapp:settings_countries')
    return redirect('myapp:settings_countries')


@login_required
@require_http_methods(["GET"])
def settings_city_add(request):
    """Модальне вікно додавання міста"""
    form = CityForm()
    countries = Country.objects.all().order_by('name')
    return render(request, 'settings/modals/city_add.html', {'form': form, 'countries': countries})


@login_required
@require_http_methods(["GET"])
def settings_city_edit(request, pk):
    """Модальне вікно редагування міста"""
    city = get_object_or_404(City, pk=pk)
    form = CityForm(instance=city)
    countries = Country.objects.all().order_by('name')
    return render(request, 'settings/modals/city_edit.html', {'form': form, 'city': city, 'countries': countries})


@login_required
@require_http_methods(["GET"])
def settings_city_delete(request, pk):
    """Модальне вікно підтвердження видалення міста"""
    city = get_object_or_404(City, pk=pk)
    companies_count = city.companies.count()
    return render(request, 'settings/modals/city_delete.html', {'city': city, 'companies_count': companies_count})


@login_required
@require_http_methods(["POST"])
def city_create(request):
    """Створення міста через HTMX"""
    form = CityForm(request.POST)
    if form.is_valid():
        city = form.save()
        messages.success(request, f'Місто "{city.name}" успішно додане.')
        if is_htmx_request(request):
            return redirect('myapp:settings_cities')
        return redirect('myapp:settings_cities')
    else:
        messages.error(request, 'Помилка валідації форми.')
        countries = Country.objects.all().order_by('name')
        return render(request, 'settings/modals/city_add.html', {'form': form, 'countries': countries}, status=400)


@login_required
@require_http_methods(["POST"])
def city_update(request, pk):
    """Оновлення міста через HTMX"""
    city = get_object_or_404(City, pk=pk)
    form = CityForm(request.POST, instance=city)
    if form.is_valid():
        city = form.save()
        messages.success(request, f'Місто "{city.name}" успішно оновлене.')
        if is_htmx_request(request):
            return redirect('myapp:settings_cities')
        return redirect('myapp:settings_cities')
    else:
        messages.error(request, 'Помилка валідації форми.')
        countries = Country.objects.all().order_by('name')
        return render(request, 'settings/modals/city_edit.html', {'form': form, 'city': city, 'countries': countries}, status=400)


@login_required
@require_http_methods(["POST"])
def city_delete(request, pk):
    """Видалення міста через HTMX"""
    city = get_object_or_404(City, pk=pk)
    companies_count = city.companies.count()
    if companies_count > 0:
        messages.error(request, f'Неможливо видалити місто "{city.name}", оскільки до нього прив\'язано {companies_count} компаній.')
        if is_htmx_request(request):
            return redirect('myapp:settings_cities')
        return redirect('myapp:settings_cities')
    
    city_name = city.name
    city.delete()
    messages.success(request, f'Місто "{city_name}" успішно видалене.')
    if is_htmx_request(request):
        return redirect('myapp:settings_cities')
    return redirect('myapp:settings_cities')


@login_required
@require_http_methods(["GET"])
def settings_category_add(request):
    """Модальне вікно додавання розділу"""
    form = CategoryForm()
    return render(request, 'settings/modals/category_add.html', {'form': form})


@login_required
@require_http_methods(["GET"])
def settings_category_edit(request, pk):
    """Модальне вікно редагування розділу"""
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)
    return render(request, 'settings/modals/category_edit.html', {'form': form, 'category': category})


@login_required
@require_http_methods(["GET"])
def settings_category_delete(request, pk):
    """Модальне вікно підтвердження видалення розділу"""
    category = get_object_or_404(Category, pk=pk)
    companies_count = category.companies.count()
    return render(request, 'settings/modals/category_delete.html', {'category': category, 'companies_count': companies_count})


@login_required
@require_http_methods(["POST"])
def category_create(request):
    """Створення категорії через HTMX"""
    form = CategoryForm(request.POST)
    if form.is_valid():
        category = form.save()
        messages.success(request, f'Розділ "{category.name}" успішно додано.')
        if is_htmx_request(request):
            return redirect('myapp:settings_categories')
        return redirect('myapp:settings_categories')
    else:
        messages.error(request, 'Помилка валідації форми.')
        return render(request, 'settings/modals/category_add.html', {'form': form}, status=400)


@login_required
@require_http_methods(["POST"])
def category_update(request, pk):
    """Оновлення категорії через HTMX"""
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
        category = form.save()
        messages.success(request, f'Розділ "{category.name}" успішно оновлено.')
        if is_htmx_request(request):
            return redirect('myapp:settings_categories')
        return redirect('myapp:settings_categories')
    else:
        messages.error(request, 'Помилка валідації форми.')
        return render(request, 'settings/modals/category_edit.html', {'form': form, 'category': category}, status=400)


@login_required
@require_http_methods(["POST"])
def category_delete(request, pk):
    """Видалення категорії через HTMX"""
    category = get_object_or_404(Category, pk=pk)
    companies_count = category.companies.count()
    if companies_count > 0:
        messages.error(request, f'Неможливо видалити розділ "{category.name}", оскільки до нього прив\'язано {companies_count} компаній.')
        if is_htmx_request(request):
            return redirect('myapp:settings_categories')
        return redirect('myapp:settings_categories')
    
    category_name = category.name
    category.delete()
    messages.success(request, f'Розділ "{category_name}" успішно видалено.')
    if is_htmx_request(request):
        return redirect('myapp:settings_categories')
    return redirect('myapp:settings_categories')


@login_required
@require_http_methods(["GET"])
def settings_status_add(request):
    """Модальне вікно додавання статусу"""
    form = StatusForm()
    return render(request, 'settings/modals/status_add.html', {'form': form})


@login_required
@require_http_methods(["GET"])
def settings_status_edit(request, pk):
    """Модальне вікно редагування статусу"""
    status = get_object_or_404(Status, pk=pk)
    form = StatusForm(instance=status)
    return render(request, 'settings/modals/status_edit.html', {'form': form, 'status': status})


@login_required
@require_http_methods(["GET"])
def settings_status_delete(request, pk):
    """Модальне вікно підтвердження видалення статусу"""
    status = get_object_or_404(Status, pk=pk)
    companies_count = status.companies.count()
    return render(request, 'settings/modals/status_delete.html', {'status': status, 'companies_count': companies_count})


@login_required
@require_http_methods(["POST"])
def status_create(request):
    """Створення статусу через HTMX"""
    form = StatusForm(request.POST)
    if form.is_valid():
        # Якщо встановлено is_default=True, скидаємо інші
        if form.cleaned_data.get('is_default'):
            Status.objects.filter(is_default=True).update(is_default=False)
        status = form.save()
        messages.success(request, f'Статус "{status.name}" успішно додано.')
        if is_htmx_request(request):
            return redirect('myapp:settings_statuses')
        return redirect('myapp:settings_statuses')
    else:
        messages.error(request, 'Помилка валідації форми.')
        return render(request, 'settings/modals/status_add.html', {'form': form}, status=400)


@login_required
@require_http_methods(["POST"])
def status_update(request, pk):
    """Оновлення статусу через HTMX"""
    status = get_object_or_404(Status, pk=pk)
    form = StatusForm(request.POST, instance=status)
    if form.is_valid():
        # Якщо встановлено is_default=True, скидаємо інші
        if form.cleaned_data.get('is_default'):
            Status.objects.filter(is_default=True).exclude(pk=pk).update(is_default=False)
        status = form.save()
        messages.success(request, f'Статус "{status.name}" успішно оновлено.')
        if is_htmx_request(request):
            return redirect('myapp:settings_statuses')
        return redirect('myapp:settings_statuses')
    else:
        messages.error(request, 'Помилка валідації форми.')
        return render(request, 'settings/modals/status_edit.html', {'form': form, 'status': status}, status=400)


@login_required
@require_http_methods(["POST"])
def status_delete(request, pk):
    """Видалення статусу через HTMX"""
    status = get_object_or_404(Status, pk=pk)
    companies_count = status.companies.count()
    if companies_count > 0:
        messages.error(request, f'Неможливо видалити статус "{status.name}", оскільки до нього прив\'язано {companies_count} компаній.')
        if is_htmx_request(request):
            return redirect('myapp:settings_statuses')
        return redirect('myapp:settings_statuses')
    
    status_name = status.name
    status.delete()
    messages.success(request, f'Статус "{status_name}" успішно видалено.')
    if is_htmx_request(request):
        return redirect('myapp:settings_statuses')
    return redirect('myapp:settings_statuses')


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
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """Модальне вікно редагування профілю + обробка POST."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено.")
            if is_htmx_request(request):
                return redirect("myapp:profile")
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

