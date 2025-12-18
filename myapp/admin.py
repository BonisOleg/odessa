from django.contrib import admin

from .models import (
    Category,
    City,
    Company,
    CompanyComment,
    CompanyPhone,
    Country,
    Status,
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "flag_emoji")
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name", "country__name", "country__code")
    ordering = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "badge_class")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "badge_class")
    list_filter = ("is_default",)
    search_fields = ("name",)
    ordering = ("name",)


class CompanyPhoneInline(admin.TabularInline):
    model = CompanyPhone
    extra = 1


class CompanyCommentInline(admin.TabularInline):
    model = CompanyComment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("client_id", "name", "city", "category", "status", "call_date")
    list_filter = ("city", "category", "status", "call_date")
    search_fields = ("client_id", "name", "keywords")
    readonly_fields = ("created_at", "updated_at")
    inlines = (CompanyPhoneInline, CompanyCommentInline)
    ordering = ("name",)


@admin.register(CompanyPhone)
class CompanyPhoneAdmin(admin.ModelAdmin):
    list_display = ("number", "company", "contact_name", "is_favorite")
    list_filter = ("is_favorite",)
    search_fields = ("number", "company__name", "contact_name")


@admin.register(CompanyComment)
class CompanyCommentAdmin(admin.ModelAdmin):
    list_display = ("company", "author_name", "created_at")
    search_fields = ("company__name", "author_name", "text")
    readonly_fields = ("created_at",)

