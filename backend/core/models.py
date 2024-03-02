from django.core.exceptions import ValidationError
from django.db import models

from .constants import (
    cashir_required_fields,
    cz_required_fields,
    ip_required_fields,
)


class Default(models.Model):
    """Default model."""

    work_time = models.FloatField("Рабочее время поумолчанию")
    sale_kpi = models.FloatField("Процент от продаж")
    hourly_rate = models.FloatField("Часовая ставка")

    def clean(self):
        """Clean data."""
        if self.id is None and Default.objects.count() > 0:
            raise ValidationError(
                "Может быть только одна запись с настройками!"
            )


class ActivitieType(models.Model):
    """ActivitieType model."""

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
    is_approved = models.BooleanField(default=False)

    @property
    def full_name(self):
        """Full name."""
        return " ".join(
            filter(None, [self.surname, self.name, self.patronymic])
        )

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
        else:
            required_fields = []
        for field in required_fields:
            if getattr(self, field) is None:
                errors[field] = "Обязательное поле!"
        if errors:
            raise ValidationError(errors)


class Document(models.Model):
    """Document model."""

    Number = models.IntegerField("Номер последнего документа", unique=True)
    start_date = models.DateField("Начало отчётного периода")
    end_date = models.DateField(
        "Конец отчётного периода", blank=True, null=True
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="employee"
    )
