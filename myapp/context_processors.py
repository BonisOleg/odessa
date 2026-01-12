"""
Контекстні процесори для глобального контексту всіх шаблонів.
"""

from .models import Country, UserProfile


def global_context(request):
    """Додає країни і профіль користувача до контексту для всіх шаблонів."""
    countries = Country.objects.all().order_by('name')
    user_profile = None
    
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            pass
    
    return {
        'countries': countries,
        'user_profile': user_profile,
    }
