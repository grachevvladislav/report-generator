import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.utils import ProgrammingError
from django.forms.models import model_to_dict

from .constants import (
    cashir_required_fields,
    cz_required_fields,
    ip_required_fields,
    stuff_required_fields,
)


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


class ActivitieType(models.Model):
    """ActivitieType model."""

    class Meta:
        """ActivitieType metaclass."""

        verbose_name = "начисление"
        verbose_name_plural = "начисления зарплаты"

    name = models.CharField("Автодействие", blank=True, null=True, unique=True)
    salary = models.IntegerField("Сумма")
    duration_in_hours = models.FloatField(
        "Длительность", blank=True, null=True
    )
    comment = models.CharField(
        "Комментарий", blank=True, null=True, unique=True
    )

    @property
    def full_name(self):
        """Full name of activitie."""
        return " ".join(filter(None, [self.name, self.comment]))


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
        NOT_TAXED = "Нет", "Не облагается налогом"

    class Role(models.TextChoices):
        """Types of system role."""

        OWNER = "Владелец", "Владелец"
        TRAINER = "Тренер", "Тренер"
        STUFF = "stuff", "stuff"
        CASHIR = "Кассир", "Кассир"
        ADMIN = "Администратор", "Администратор"

    surname = models.CharField("Фамилия", blank=True, null=True)
    name = models.CharField("Имя")
    patronymic = models.CharField("Отчество", blank=True, null=True)
    inn = models.CharField(
        "ИНН", max_length=10, unique=True, blank=True, null=True
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
    ogrnip = models.DecimalField(
        "ОГРНИП",
        max_digits=20,
        decimal_places=0,
        blank=True,
        null=True,
        unique=True,
    )
    agreement_number = models.IntegerField(
        "Номер договора", blank=True, null=True, unique=True
    )
    agreement_date = models.DateField(
        "Дата заключения догвора", blank=True, null=True
    )
    telegram_id = models.IntegerField(
        "Telegram id", blank=True, null=True, unique=True
    )
    tax_regime = models.CharField(
        max_length=3, choices=TaxRegime.choices, default=TaxRegime.CZ
    )
    role = models.CharField(
        max_length=13, choices=Role.choices, default=Role.TRAINER
    )
    is_active = models.BooleanField(default=True)

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

    @property
    def full_value(self):
        """Full value for report."""
        if self.tax_regime == self.TaxRegime.CZ:
            return (
                f"{self.tax_regime} {self.surname} {self.name} "
                f"{self.patronymic}, ИНН: {self.inn}, {self.address}, р/с "
                f"{self.checking_account}, {self.bank}, БИК: {self.bik}, "
                f"к/с {self.correspondent_account}"
            )
        else:
            return (
                f"{self.tax_regime} {self.surname} {self.name} "
                f"{self.patronymic}, ОГРНИП: {self.ogrnip}, ИНН: {self.inn}"
                f", {self.address}, р/с {self.checking_account}, "
                f"{self.bank}, БИК: {self.bik}, к/с "
                f"{self.correspondent_account}"
            )

    def __str__(self):
        return self.display_name

    def clean(self):
        """Clean data."""
        if (
            self.id is None
            and self.role is Employee.Role.OWNER.value
            and Employee.objects.filter(role=Employee.Role.OWNER).count() > 0
        ):
            raise ValidationError("Может быть только один владелец!")
        if (
            self.id is None
            and self.role is Employee.Role.CASHIR.value
            and Employee.objects.filter(role=Employee.Role.CASHIR).count() > 0
        ):
            raise ValidationError("Может быть только один кассир!")
        errors = {}
        if self.tax_regime == self.TaxRegime.IP:
            required_fields = ip_required_fields
        elif self.tax_regime == self.TaxRegime.CZ:
            required_fields = cz_required_fields
        elif self.role == self.Role.CASHIR:
            required_fields = cashir_required_fields
        elif self.role == self.Role.STUFF:
            required_fields = stuff_required_fields
        else:
            required_fields = []
        for field in required_fields:
            if getattr(self, field) is None:
                errors[field] = "Обязательное поле!"
        if errors:
            raise ValidationError(errors)


class Document(models.Model):
    """Document model."""

    class Meta:
        """Document metaclass."""

        verbose_name = "отчет"
        verbose_name_plural = "отчеты"

    number = models.IntegerField("Номер документа", unique=True)
    start_date = models.DateField("Начало отчётного периода")
    end_date = models.DateField("Конец отчётного периода")
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="document"
    )


class Schedule(models.Model):
    """Schedule model."""

    class Meta:
        """Schedule metaclass."""

        verbose_name = "запись"
        verbose_name_plural = "рабочий график"

    date = models.DateField("Дата")
    employee = models.ForeignKey(
        Employee,
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
        if self.employee:
            return ", ".join(
                [
                    self.date.strftime("%d %B %Y"),
                    self.employee.full_name,
                    str(self.time),
                ]
            )
        else:
            return ", ".join(
                [
                    self.date.strftime("%d %B %Y"),
                    "---------",
                    str(self.time),
                ]
            )

    def _complete_symbol(self) -> str:
        if datetime.datetime.today() > self.date:
            return "✅"
        else:
            return "☑️"

    def full_string(self, full: bool = True) -> str:
        """Return all info in string."""
        if full:
            return " ".join(
                [
                    self._complete_symbol,
                    self.date.strftime("%d %B"),
                    self.employee.key_name,
                    "\n",
                ]
            )
        else:
            return " ".join(
                [
                    self._complete_symbol,
                    self.date.strftime("%d %B"),
                    "\n",
                ]
            )


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
