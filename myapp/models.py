from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Country(models.Model):
    """Довідник країн (для налаштувань і прив'язки міст/користувачів)."""

    name: str = models.CharField(max_length=100, unique=True)
    code: str = models.CharField(max_length=10, unique=True)
    flag_emoji: str = models.CharField(max_length=8, blank=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover - тривіальний метод
        return self.name


class City(models.Model):
    """Довідник міст."""

    name: str = models.CharField(max_length=100)
    country: Country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="cities",
    )

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        unique_together = ("name", "country")
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.country.code})"


class Category(models.Model):
    """Розділ/категорія компанії з кольором бейджа."""

    name: str = models.CharField(max_length=100, unique=True)
    badge_color_bg: str = models.CharField(
        max_length=16,
        default="#E5E7EB",
        help_text="HEX колір фону бейджа",
    )
    badge_color_fg: str = models.CharField(
        max_length=16,
        default="#111827",
        help_text="HEX колір тексту бейджа",
    )
    badge_class: str = models.CharField(
        max_length=64,
        default="badge--custom-blue",
        help_text="CSS клас бейджа для сумісності з існуючими стилями",
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Status(models.Model):
    """Статус компанії з кольором/класом бейджа."""

    name: str = models.CharField(max_length=100, unique=True)
    is_default: bool = models.BooleanField(default=False)
    badge_class: str = models.CharField(
        max_length=64,
        default="badge--secondary",
        help_text="CSS клас бейджа (badge--success, badge--warning тощо)",
    )

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Company(models.Model):
    """Основна сутність компанії."""

    client_id: str = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        help_text="Зовнішній ID клієнта, наприклад #00123. Генерується автоматично.",
    )
    name: str = models.CharField(max_length=255)

    city: City | None = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="companies",
        null=True,
        blank=True,
    )
    category: Category | None = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="companies",
        null=True,
        blank=True,
    )
    status: Status | None = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="companies",
        null=True,
        blank=True,
    )

    telegram: str = models.CharField(max_length=255, blank=True)
    website: str = models.URLField(blank=True)
    instagram: str = models.CharField(max_length=255, blank=True)

    short_comment: str = models.CharField(max_length=500, blank=True)
    full_description: str = models.TextField(blank=True)

    keywords: str = models.TextField(
        blank=True,
        help_text="Ключові слова через кому для пошуку",
    )

    call_date = models.DateField(
        null=True,
        blank=True,
        help_text="Запланована дата дзвінка",
    )

    logo = models.ImageField(
        upload_to='companies/logos/',
        blank=True,
        null=True,
        help_text="Логотип компанії"
    )

    photos = models.JSONField(
        default=list,
        blank=True,
        help_text="Список URL фотографій компанії (JSON array)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Генерує client_id, якщо він не заданий."""
        if not self.client_id:
            last_id = (
                Company.objects.order_by("-id")
                .values_list("id", flat=True)
                .first()
            )
            next_number = (last_id or 0) + 1
            self.client_id = f"#{next_number:05d}"
        super().save(*args, **kwargs)

    @property
    def status_badge_class(self) -> str:
        """CSS-клас бейджа статусу для використання у шаблонах."""
        if self.status and self.status.badge_class:
            return self.status.badge_class
        return "badge--secondary"

    @property
    def category_badge_class(self) -> str:
        """CSS-клас бейджа категорії (можна використати у майбутньому)."""
        if self.category and self.category.badge_class:
            return self.category.badge_class
        return "badge--secondary"

    @property
    def call_date_display(self) -> str:
        """Форматована дата дзвінка для відображення."""
        if self.call_date:
            return self.call_date.strftime("%d.%m.%Y")
        return "Не встановлено"

    @property
    def created_date(self) -> str:
        """Форматована дата створення для відображення."""
        if self.created_at:
            return self.created_at.strftime("%d.%m.%Y")
        return ""

    @property
    def updated_date(self) -> str:
        """Форматована дата оновлення для відображення."""
        if self.updated_at:
            return self.updated_at.strftime("%d.%m.%Y")
        return ""

    @property
    def status_badge(self) -> str:
        """CSS-клас бейджа статусу (alias для status_badge_class)."""
        return self.status_badge_class


class CompanyPhone(models.Model):
    """Телефон компанії з іменем контакту та ознакою обраного."""

    company: Company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="phones",
    )
    number: str = models.CharField(max_length=32)
    contact_name: str = models.CharField(max_length=255, blank=True)
    is_favorite: bool = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company phone"
        verbose_name_plural = "Company phones"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.number} ({self.company.name})"


class CompanyComment(models.Model):
    """Коментар до компанії (історія взаємодій)."""

    company: Company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author_name: str = models.CharField(max_length=255)
    text: str = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company comment"
        verbose_name_plural = "Company comments"
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.author_name}: {self.text[:50]}"


class CompanyAddress(models.Model):
    """Адреса компанії з іменем та ознакою обраного."""
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    address = models.CharField(max_length=500)
    is_favorite = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Company address"
        verbose_name_plural = "Company addresses"
    
    def __str__(self) -> str:  # pragma: no cover
        return f"{self.address} ({self.company.name})"


class UserProfile(models.Model):
    """Профіль користувача з роллю, країною та аватаром."""
    
    ROLE_SUPER_ADMIN = 'SUPER_ADMIN'
    ROLE_OBSERVER = 'OBSERVER'
    ROLE_MANAGER = 'MANAGER'
    
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Супер адмін'),
        (ROLE_OBSERVER, 'Спостерігач'),
        (ROLE_MANAGER, 'Менеджер'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MANAGER,
        help_text="Роль користувача в системі"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Призначена країна для користувача"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Аватар користувача"
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    language = models.CharField(
        max_length=10,
        default='ru',
        help_text="Мова інтерфейсу (ru, en, uk)"
    )
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ("user__username",)
    
    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def is_super_admin(self) -> bool:
        """Перевірка чи користувач є супер адміном."""
        return self.role == self.ROLE_SUPER_ADMIN
    
    @property
    def is_observer(self) -> bool:
        """Перевірка чи користувач є спостерігачем."""
        return self.role == self.ROLE_OBSERVER
    
    @property
    def is_manager(self) -> bool:
        """Перевірка чи користувач є менеджером."""
        return self.role == self.ROLE_MANAGER


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматичне створення профілю при створенні користувача."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Автоматичне збереження профілю при збереженні користувача."""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


class UserFavoriteCompany(models.Model):
    """Обрана компанія користувача (для ранжування)."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_companies'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Favorite Company"
        verbose_name_plural = "User Favorite Companies"
        unique_together = ('user', 'company')
        ordering = ('-created_at',)
    
    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} → {self.company.name}"

