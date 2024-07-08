import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.utils import ProgrammingError
from django.forms.models import model_to_dict

from .validators import exclude_future_dates, passport_series_validator


class Default(models.Model):
    """Default model."""

    class Meta:
        """Default metaclass."""

        verbose_name = "настройка"
        verbose_name_plural = "настройки"

    work_time = models.FloatField("Рабочее время по умолчанию")
    planning_horizon = models.IntegerField(
        "Горизонт планирования (дни)",
        validators=[
            MinValueValidator(1),
        ],
    )
    cashier_telegram_id = models.IntegerField("Telegram id для чеков")
    mark_emails_as_read = models.BooleanField(
        "Отмечать письма прочитанными", default=False
    )

    def clean(self):
        """Clean data."""
        if self.id is None and Default.objects.acount() > 0:
            raise ValidationError(
                "Может быть только одна запись с настройками!"
            )

    @classmethod
    def get_default(cls, key):
        """Get dict of default project settings."""
        try:
            first_record = cls.objects.first()
        except ProgrammingError:
            return None
        if first_record:
            return model_to_dict(first_record)[key]
        else:
            return None


class Employee(models.Model):
    """Employee model."""

    class Meta:
        """Employee metaclass."""

        verbose_name = "сотрудник"
        verbose_name_plural = "сотрудники"

    class TaxRegime(models.TextChoices):
        """Types of tax regime."""

        IP = "ИП", "Индивидуальный предприниматель"
        CZ = "СЗ", "Самозанятый"

    base_required_fields = [
        "inn",
        "email",
        "tax_regime",
        "address",
        "checking_account",
        "bank",
        "bik",
        "correspondent_account",
    ]
    required_fields_by_tax = {
        TaxRegime.CZ: [
            "issued_by",
            "date_of_issue",
            "department_code",
            "passport_series",
            "passport_number",
        ],
        TaxRegime.IP: [
            "ogrnip",
        ],
    }

    surname = models.CharField("Фамилия", blank=True, null=True)
    name = models.CharField("Имя")
    patronymic = models.CharField("Отчество", blank=True, null=True)
    inn = models.CharField(
        "ИНН",
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        help_text="10 или 12 цифр",
    )
    tax_registration_date = models.DateField(
        "Дата регистрации в качестве плательщика НПД", blank=True, null=True
    )
    tax_regime = models.CharField(
        "Режим налогообложения",
        choices=TaxRegime.choices,
        default=TaxRegime.CZ,
    )
    ogrnip = models.DecimalField(
        "ОГРНИП",
        max_digits=20,
        decimal_places=0,
        blank=True,
        null=True,
        unique=True,
        help_text="14 цифр",
    )
    address = models.CharField("Адрес, как в паспорте", blank=True, null=True)
    checking_account = models.DecimalField(
        "Номер счёта",
        max_digits=20,
        decimal_places=0,
        unique=True,
        blank=True,
        null=True,
    )
    bank = models.CharField(
        "Название банка", blank=True, null=True, help_text="ПАО ВТБ"
    )
    bik = models.CharField("БИК", blank=True, null=True, help_text="9 цифр")
    correspondent_account = models.DecimalField(
        "Кор. счёт", max_digits=20, decimal_places=0, blank=True, null=True
    )
    passport_series = models.CharField(
        "Серия паспорта",
        max_length=4,
        validators=[
            passport_series_validator,
        ],
        blank=True,
        null=True,
        help_text="4520 (4 цифр)",
    )
    passport_number = models.CharField(
        "Номер паспорта",
        max_length=6,
        blank=True,
        null=True,
        help_text="123342 (6 цифр)",
    )
    issued_by = models.CharField("Кем выдан", blank=True, null=True)
    date_of_issue = models.DateField(
        "Дата выдачи",
        validators=[
            exclude_future_dates,
        ],
        blank=True,
        null=True,
    )
    department_code = models.CharField(
        "Код подразделения",
        max_length=6,
        blank=True,
        null=True,
        help_text="660003 (6 цифр)",
    )
    email = models.CharField(
        "Email",
        unique=True,
        blank=True,
        null=True,
        help_text="john.smith@example.com",
    )
    telegram_id = models.IntegerField(
        "Telegram id",
        blank=True,
        null=True,
        unique=True,
        help_text="1234567890 (10 цифр)",
    )
    gdpr_is_signed = models.BooleanField("Обработка ПД", default=False)
    is_active = models.BooleanField("Сотрудник активен", default=True)
    is_stuff = models.BooleanField("Права суперпользователя", default=False)
    is_owner = models.BooleanField("Владелец", default=False)

    def for_doc(self):
        """Get complete information to create a document."""
        if self.tax_regime == self.TaxRegime.CZ:
            return (
                f"{self.tax_regime} {self.full_name}, ИНН: {self.inn}, "
                f"{self.address}, р/с {self.checking_account}, "
                f"{self.bank}, БИК: {self.bik}, к/с "
                f"{self.correspondent_account}\n\n"
            )
        if self.tax_regime == self.TaxRegime.IP:
            return (
                f"{self.tax_regime} {self.full_name}, ОГРНИП: {self.ogrnip}, "
                f"ИНН: {self.inn}, "
                f"{self.address}, р/с {self.checking_account}, "
                f"{self.bank}, БИК: {self.bik}, к/с "
                f"{self.correspondent_account}\n\n"
            )

    @property
    def full_name(self):
        """Full name."""
        return " ".join(
            filter(None, [self.surname, self.name, self.patronymic])
        )

    @property
    def key_name(self) -> str:
        """Key name for documents."""
        return f"{self.surname} {self.name[0]}."

    @property
    def short_name(self) -> str:
        """Last name I.O."""
        return f"{self.surname} {self.name[0]}.{self.patronymic[0]}."

    def __str__(self):
        return self.full_name

    def clean(self):
        """Clean data."""
        if (
            self.id is None
            and Employee.objects.filter(is_owner=True).count() > 0
        ):
            raise ValidationError("Может быть только один владелец!")
        errors = {}
        required_fields = [
            "name",
            "surname",
            "patronymic",
        ]
        if self.is_stuff:
            pass
        else:
            required_fields.extend(self.base_required_fields)
            required_fields.extend(
                self.required_fields_by_tax[self.tax_regime]
            )
        for field in required_fields:
            if getattr(self, field) is None:
                errors[field] = "Обязательное поле!"
        if errors:
            raise ValidationError(errors)


class Schedule(models.Model):
    """Schedule model."""

    class Meta:
        """Schedule metaclass."""

        verbose_name = "запись"
        verbose_name_plural = "рабочий график"

        unique_together = (
            "date",
            "second_employee",
        )

    date = models.DateField("Дата")
    employee = models.ForeignKey(
        Employee,
        verbose_name="Сотрудник",
        on_delete=models.CASCADE,
        related_name="schedule",
        blank=True,
        null=True,
        default=None,
    )
    time = models.FloatField(
        "Рабочее время",
        blank=True,
        null=True,
        default=Default.get_default("work_time"),
    )
    second_employee = models.BooleanField(
        "Второй сотрудник на смене", default=False
    )

    def __str__(self):
        return self.full_string(full=True)

    def _complete_symbol(self) -> str:
        if datetime.date.today() > self.date:
            return "✅"
        else:
            return "☑️"

    def get_employee_name(self):
        """Get key name if employee exist."""
        if self.employee:
            return self.employee.key_name
        else:
            return "----"

    def full_string(self, full: bool = False) -> str:
        """Return all info in string."""
        if full:
            employee_name = self.get_employee_name()
            return " ".join(
                [
                    self._complete_symbol(),
                    self.date.strftime("%d %B"),
                    employee_name[0],
                ]
            )
        else:
            return " ".join(
                [self._complete_symbol(), self.date.strftime("%d %B")]
            )

    full_string.short_description = "Дата"


class BotRequest(models.Model):
    """Requests from users model."""

    class Meta:
        """Requests from users metaclass."""

        verbose_name = "запрос"
        verbose_name_plural = "запросы пользователей"

    telegram_id = models.IntegerField("Telegram id", unique=True)
    username = models.CharField("username")
    first_name = models.CharField("Имя", blank=True, null=True)
    last_name = models.CharField("Фамилия", blank=True, null=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="bot_request",
        blank=True,
        null=True,
        default=None,
    )

    @property
    def full_name(self):
        """Contact first name and last name."""
        return f"{self.first_name or " - "} {self.last_name or " - "}"

    def __str__(self):
        """Str method."""
        return self.full_name

    def save(self, *args, **kwargs):
        """Add telegram id to employee instance and remove request."""
        if self.employee:
            self.employee.telegram_id = self.telegram_id
            self.employee.save()
            self.delete()
        else:
            super().save(*args, **kwargs)
