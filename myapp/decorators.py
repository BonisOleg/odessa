"""
Декоратори для обмеження доступу по ролях.
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse


def super_admin_required(view_func):
    """Декоратор для перевірки чи користувач є супер адміном."""
    @wraps(view_func)
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(request.user, 'userprofile'):
            return redirect('myapp:company_list')
        if not request.user.userprofile.is_super_admin:
            return redirect('myapp:company_list')
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_or_super_admin_required(view_func):
    """Декоратор для перевірки чи користувач є менеджером або супер адміном."""
    @wraps(view_func)
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(request.user, 'userprofile'):
            return redirect('myapp:company_list')
        if request.user.userprofile.is_observer:
            return redirect('myapp:company_list')
        return view_func(request, *args, **kwargs)
    return wrapper


def observer_can_view(view_func):
    """Декоратор для перевірки доступу - спостерігач може тільки переглядати."""
    @wraps(view_func)
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Спостерігач може переглядати, але не редагувати
        # Цей декоратор використовується для GET запитів
        if request.method == 'POST':
            if hasattr(request.user, 'userprofile') and request.user.userprofile.is_observer:
                return redirect('myapp:company_list')
        return view_func(request, *args, **kwargs)
    return wrapper

