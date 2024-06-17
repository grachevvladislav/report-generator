import asyncio
import datetime

from asgiref.sync import async_to_sync, sync_to_async
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
    cashier_telegram_id = models.IntegerField("Telegram id")

    async def clean(self):
        """Clean data."""
        if self.id is None and await Default.objects.acount() > 0:
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

    surname = models.CharField("Фамилия", blank=True, null=True)
    name = models.CharField("Имя")
    patronymic = models.CharField("Отчество", blank=True, null=True)
    inn = models.CharField(
        "ИНН", max_length=12, unique=True, blank=True, null=True
    )
    email = models.CharField("Email")
    tax_regime = models.CharField(
        choices=TaxRegime.choices, default=TaxRegime.CZ
    )
    ogrnip = models.DecimalField(
        "ОГРНИП",
        max_digits=20,
        decimal_places=0,
        blank=True,
        null=True,
        unique=True,
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
    bank = models.CharField("Название банка", blank=True, null=True)
    bik = models.CharField("БИК", blank=True, null=True)
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
    )
    passport_number = models.CharField(
        "Номер паспорта", max_length=6, blank=True, null=True
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
        "Кем выдан", max_length=7, blank=True, null=True
    )

    telegram_id = models.IntegerField(
        "Telegram id", blank=True, null=True, unique=True
    )
    is_active = models.BooleanField(default=True)
    is_stuff = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

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
    def display_name(self):
        """Admin site display name."""
        if self.is_active:
            return self.full_name
        else:
            return " ".join([self.full_name, "⛔️"])

    def __str__(self):
        return self.display_name

    # def clean(self):
    #     """Clean data."""
    #     if (
    #         self.id is None
    #         and self.role is Employee.Role.OWNER.value
    #         and Employee.objects.filter(role=Employee.Role.OWNER).count() > 0
    #     ):
    #         raise ValidationError("Может быть только один владелец!")
    #     if (
    #         self.id is None
    #         and self.role is Employee.Role.CASHIR.value
    #         and Employee.objects.filter(role=Employee.Role.CASHIR).count() > 0
    #     ):
    #         raise ValidationError("Может быть только один кассир!")
    #     errors = {}
    #     if self.tax_regime == self.TaxRegime.NOT_TAXED:
    #         required_fields = [
    #             "name",
    #         ]
    #     else:
    #         required_fields = base_required_fields
    #
    #     if self.tax_regime == self.TaxRegime.IP:
    #         required_fields.extend(ip_required_fields)
    #
    #     for field in required_fields:
    #         if getattr(self, field) is None:
    #             errors[field] = "Обязательное поле!"
    #     if errors:
    #         raise ValidationError(errors)


class Schedule(models.Model):
    """Schedule model."""

    class Meta:
        """Schedule metaclass."""

        verbose_name = "запись"
        verbose_name_plural = "рабочий график"

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

    def __str__(self):
        return async_to_sync(self.full_string_async)(full=True)

    def _complete_symbol(self) -> str:
        if datetime.date.today() > self.date:
            return "✅"
        else:
            return "☑️"

    @sync_to_async
    def get_employee_name(self):
        """Get key name if employee exist."""
        if self.employee:
            return self.employee.key_name
        else:
            return "----"

    async def full_string_async(self, full: bool = False) -> str:
        """Return all info in string."""
        if full:
            employee_name = await asyncio.gather(self.get_employee_name())
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

    def full_string(self, full: bool = False) -> str:
        """Return all info in string (sync)."""
        return async_to_sync(self.full_string_async)()

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
