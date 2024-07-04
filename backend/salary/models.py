import datetime
from decimal import Decimal

from core.models import Employee
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from utils import (
    first_day_of_the_previous_month,
    last_day_of_the_previous_month,
)


class ContractTemplate(models.Model):
    """ContractTemplate model."""

    class Meta:
        """ContractTemplate metaclass."""

        verbose_name = "шаблон"
        verbose_name_plural = "шаблоны договоров"

    name = models.CharField("Название")
    description = models.CharField("Описание", null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    file_data = models.BinaryField(null=True)
    is_active = models.BooleanField("Шаблон активен", default=True)

    def __str__(self):
        return self.name


def get_new_contract_number():
    last_number = Contract.objects.aggregate(models.Max("number"))[
        "number__max"
    ]
    if last_number:
        return last_number + 1
    return 1


class Contract(models.Model):
    """Contract model."""

    class Meta:
        """Contract metaclass."""

        verbose_name = "договор"
        verbose_name_plural = "договоры"
        unique_together = ("employee", "template")

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="сontract",
        verbose_name="Сотрудник",
    )
    template = models.ForeignKey(
        ContractTemplate,
        on_delete=models.CASCADE,
        related_name="сontract",
        default=None,
        verbose_name="Шаблон договора",
    )
    original_signed = models.BooleanField("Оригинал подписан", default=False)
    number = models.IntegerField(
        "Номер договора",
        unique=True,
        default=get_new_contract_number,
        validators=[
            MinValueValidator(1),
        ],
    )
    start_date = models.DateField(
        "Дата заключения договора", default=datetime.datetime.today
    )
    end_date = models.DateField(
        "Дата окончания договора", blank=True, null=True
    )

    def clean(self):
        """Validate start | end date."""
        super().clean()
        errors = {}
        if self.end_date and self.start_date > self.end_date:
            errors["start_date"] = "Дата начала не может быть позже конца!"
            raise ValidationError(errors)

    @property
    def is_active(self):
        """Current status of the contract."""
        if self.end_date:
            return datetime.date.today() <= self.end_date
        return True

    is_active.fget.boolean = True

    @property
    def display_name(self):
        """Admin site display name."""
        if self.is_active:
            return f"#{self.number} {self.employee.full_name}"
        else:
            return f"#{self.number} {self.employee.full_name} ⛔"

    def __str__(self):
        return self.display_name


def get_new_salary_certificate_number():
    last_number = SalaryCertificate.objects.aggregate(models.Max("number"))[
        "number__max"
    ]
    if last_number:
        return last_number + 1
    return 1


class SalaryCertificate(models.Model):
    """SalaryCertificate model."""

    class Meta:
        """SalaryCertificate metaclass."""

        verbose_name = "зарплатный акт"
        verbose_name_plural = "зарплатные акты"

    number = models.IntegerField(
        "Номер документа",
        unique=True,
        default=get_new_salary_certificate_number,
    )
    start_date = models.DateField(
        "Начало отчётного периода", default=first_day_of_the_previous_month
    )
    end_date = models.DateField(
        "Конец отчётного периода", default=last_day_of_the_previous_month
    )
    date_of_creation = models.DateField(
        "Дата создания", default=datetime.datetime.today
    )
    original_signed = models.BooleanField("Оригинал подписан", default=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="salary_certificate",
        verbose_name="договор",
    )

    def __str__(self):
        value = " ".join(
            map(
                str,
                [
                    self.number,
                    self.start_date,
                    self.contract.employee.full_name,
                ],
            )
        )
        if self.original_signed:
            return value
        return value + " ❗️"


class Rate(models.Model):
    """Rate rule for ContractTemplate."""

    class Meta:
        """Rate metaclass."""

        verbose_name = "ставка"
        verbose_name_plural = "Правило: Ставка"

    name = models.CharField("Название")
    value = models.IntegerField(
        "Сумма",
        validators=[
            MinValueValidator(0),
        ],
    )
    contract = models.ForeignKey(
        ContractTemplate, on_delete=models.CASCADE, related_name="rate"
    )

    def __str__(self):
        return f"{self.name} {self.value}р."


class AmountOfAccrual(models.Model):
    """
    AmountOfAccrual rule for ContractTemplate.

    If ContractTemplate object has one or more connections with AmountOfAccrual.
    -> We look for all accruals for the employee and add required fields.
    """

    class Meta:
        """AmountOfAccrual metaclass."""

        verbose_name = "Сумма начислений"
        verbose_name_plural = "Правило: Сумма начислений"
        unique_together = ("required_field", "contract")

    required_field = models.CharField(
        "Обязательное поле", blank=True, null=True
    )
    contract = models.ForeignKey(
        ContractTemplate,
        on_delete=models.CASCADE,
        related_name="amount_of_accrual",
    )

    def __str__(self):
        return " ".join([self.required_field, self.contract.name])


class PercentageOfSales(models.Model):
    """
    PercentageOfSales rule for ContractTemplate.

    Percentage of personal sales for the selected period.
    """

    class Meta:
        """PercentageOfSales metaclass."""

        verbose_name = "Правило: Процент от личных продаж"

    name = models.CharField("Название")
    percentage_value = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal(0),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    contract = models.OneToOneField(
        ContractTemplate,
        on_delete=models.CASCADE,
        related_name="percentage_of_sales",
    )

    def __str__(self):
        return f"{self.name} {self.percentage_value}%"


class HourlyPayment(models.Model):
    """
    HourlyPayment rule for ContractTemplate.

    Payment for the time of work specified in the schedule.
    """

    class Meta:
        """PercentageOfSales metaclass."""

        verbose_name = "Правило: Почасовая ставка"

    name = models.CharField("Название")
    contract = models.OneToOneField(
        ContractTemplate,
        on_delete=models.CASCADE,
        related_name="hourly_payment",
    )

    def __str__(self):
        return self.name
