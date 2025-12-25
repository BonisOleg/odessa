"""
URL Configuration для CRM Nice
"""

from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Компанії
    path('companies/', views.company_list, name='company_list'),
    path('companies/add/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('companies/<int:pk>/update-short-comment/', views.company_update_short_comment, name='company_update_short_comment'),
    path('companies/<int:pk>/update-call-date/', views.company_update_call_date, name='company_update_call_date'),
    path('companies/<int:pk>/comments/add/', views.company_comment_add, name='company_comment_add'),
    path('companies/<int:pk>/comments/<int:comment_id>/delete/', views.company_comment_delete, name='company_comment_delete'),
    path('companies/<int:pk>/delete-logo/', views.company_delete_logo, name='company_delete_logo'),
    path('companies/<int:pk>/delete-photo/', views.company_delete_photo, name='company_delete_photo'),
    path('companies/<int:pk>/export/', views.company_export, name='company_export'),
    path('companies/<int:pk>/toggle-favorite/', views.company_toggle_favorite, name='company_toggle_favorite'),
    path('companies/check-duplicates/', views.company_check_duplicates, name='company_check_duplicates'),
    path('api/cities-by-country/', views.get_cities_by_country, name='get_cities_by_country'),
    
    # Налаштування
    path('settings/', views.settings_dashboard, name='settings_dashboard'),
    path('settings/countries/', views.settings_countries, name='settings_countries'),
    path('settings/countries/add/', views.settings_country_add, name='settings_country_add'),
    path('settings/countries/create/', views.country_create, name='country_create'),
    path('settings/countries/<int:pk>/edit/', views.settings_country_edit, name='settings_country_edit'),
    path('settings/countries/<int:pk>/update/', views.country_update, name='country_update'),
    path('settings/countries/<int:pk>/delete/', views.settings_country_delete, name='settings_country_delete'),
    path('settings/countries/<int:pk>/delete/confirm/', views.country_delete, name='country_delete'),
    path('settings/cities/', views.settings_cities, name='settings_cities'),
    path('settings/cities/add/', views.settings_city_add, name='settings_city_add'),
    path('settings/cities/create/', views.city_create, name='city_create'),
    path('settings/cities/<int:pk>/edit/', views.settings_city_edit, name='settings_city_edit'),
    path('settings/cities/<int:pk>/update/', views.city_update, name='city_update'),
    path('settings/cities/<int:pk>/delete/', views.settings_city_delete, name='settings_city_delete'),
    path('settings/cities/<int:pk>/delete/confirm/', views.city_delete, name='city_delete'),
    path('settings/categories/', views.settings_categories, name='settings_categories'),
    path('settings/categories/add/', views.settings_category_add, name='settings_category_add'),
    path('settings/categories/create/', views.category_create, name='category_create'),
    path('settings/categories/<int:pk>/edit/', views.settings_category_edit, name='settings_category_edit'),
    path('settings/categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('settings/categories/<int:pk>/delete/', views.settings_category_delete, name='settings_category_delete'),
    path('settings/categories/<int:pk>/delete/confirm/', views.category_delete, name='category_delete'),
    path('settings/statuses/', views.settings_statuses, name='settings_statuses'),
    path('settings/statuses/add/', views.settings_status_add, name='settings_status_add'),
    path('settings/statuses/create/', views.status_create, name='status_create'),
    path('settings/statuses/<int:pk>/edit/', views.settings_status_edit, name='settings_status_edit'),
    path('settings/statuses/<int:pk>/update/', views.status_update, name='status_update'),
    path('settings/statuses/<int:pk>/delete/', views.settings_status_delete, name='settings_status_delete'),
    path('settings/statuses/<int:pk>/delete/confirm/', views.status_delete, name='status_delete'),
    path('settings/users/', views.settings_users, name='settings_users'),
    path('settings/users/add/', views.settings_user_add, name='settings_user_add'),
    path('settings/users/create/', views.user_create, name='user_create'),
    path('settings/users/<int:pk>/edit/', views.settings_user_edit, name='settings_user_edit'),
    path('settings/users/<int:pk>/delete/', views.settings_user_delete, name='settings_user_delete'),
    
    # Заглушки для розділів в розробці
    path('clients/', views.stub_page, name='clients'),
    path('tasks/', views.stub_page, name='tasks'),
    path('sales/', views.stub_page, name='sales'),
    path('seo/', views.stub_page, name='seo'),
    path('franchises/', views.stub_page, name='franchises'),
    path('finances/', views.stub_page, name='finances'),
    
    # Accounts
    path('accounts/login/', views.login_page, name='login'),
    path('accounts/profile/', views.profile_page, name='profile'),
    path('accounts/profile/edit/', views.profile_edit, name='profile_edit'),
    path('accounts/logout/', views.logout_view, name='logout'),
]
