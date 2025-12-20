from __future__ import annotations

from typing import Iterable

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Category, City, Country, Company, Status


class CompanyForm(forms.ModelForm):
    """Форма для створення/редагування компанії.

    Телефони, коментарі та фото обробляються окремо, щоб зберегти існуючу верстку.
    """

    class Meta:
        model = Company
        fields: Iterable[str] = (
            "name",
            "city",
            "category",
            "status",
            "telegram",
            "website",
            "instagram",
            "short_comment",
            "full_description",
            "call_date",
            "keywords",
            "logo",
        )

        widgets = {
            "call_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }


class LoginForm(forms.Form):
    """Проста форма логіну під поточну верстку (username/password)."""

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self) -> dict:
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Невірний логін або пароль.")
            if not user.is_active:
                raise forms.ValidationError("Обліковий запис деактивовано.")
            cleaned_data["user"] = user
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Редагування базових полів профілю користувача."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class CountryForm(forms.ModelForm):
    """Форма для створення/редагування країни."""

    class Meta:
        model = Country
        fields = ("name", "code", "flag_emoji")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Украина"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "UA", "maxlength": "2"}),
            "flag_emoji": forms.TextInput(attrs={"class": "form-control", "placeholder": "🇺🇦"}),
        }

    def clean_code(self) -> str:
        """Валідація коду країни (має бути 2 символи)."""
        code = self.cleaned_data.get("code", "").strip().upper()
        if code and len(code) != 2:
            raise forms.ValidationError("Код країни має бути 2 символи.")
        return code


class CityForm(forms.ModelForm):
    """Форма для створення/редагування міста."""

    class Meta:
        model = City
        fields = ("name", "country")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Киев"}),
            "country": forms.Select(attrs={"class": "form-control"}),
        }


class CategoryForm(forms.ModelForm):
    """Форма для створення/редагування категорії."""

    class Meta:
        model = Category
        fields = ("name", "badge_color_bg", "badge_color_fg")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "IT-услуги"}),
            "badge_color_bg": forms.TextInput(attrs={"type": "color", "class": "form-control", "value": "#3B82F6"}),
            "badge_color_fg": forms.TextInput(attrs={"type": "color", "class": "form-control", "value": "#FFFFFF"}),
        }


class StatusForm(forms.ModelForm):
    """Форма для створення/редагування статусу."""

    class Meta:
        model = Status
        fields = ("name", "is_default", "badge_class")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "В работе"}),
            "is_default": forms.CheckboxInput(attrs={"class": "form-control"}),
            "badge_class": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["badge_class"].choices = [
            ("badge--secondary", "Сірий"),
            ("badge--primary", "Синій"),
            ("badge--success", "Зелений"),
            ("badge--warning", "Жовтий"),
            ("badge--danger", "Червоний"),
        ]

