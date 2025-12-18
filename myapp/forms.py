from __future__ import annotations

from typing import Iterable

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Company


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

