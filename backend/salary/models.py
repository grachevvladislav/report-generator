from decimal import Decimal

from core.models import Employee
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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
    is_active = models.BooleanField("Договор действует", default=True)
    original_signed = models.BooleanField("Оригинал подписан", default=False)
    number = models.IntegerField(
        "Номер договора",
        unique=True,
        default=get_new_contract_number,
        validators=[
            MinValueValidator(1),
        ],
    )
    start_date = models.DateField("Дата заключения договора")
    end_date = models.DateField(
        "Дата окончания договора", blank=True, null=True
    )

    @property
    def full_value(self):
        """Full value for report."""
        if self.tax_regime == self.TaxRegime.CZ:
            return (
                f"{self.tax_regime} {self.employee.surname} "
                f"{self.employee.name} {self.employee.patronymic}, ИНН: "
                f"{self.employee.inn}, {self.employee.address}, р/с "
                f"{self.employee.checking_account}, {self.employee.bank}, БИК: "
                f"{self.employee.bik}, к/с "
                f"{self.employee.correspondent_account}"
            )
        else:
            return (
                f"{self.tax_regime} {self.employee.surname} "
                f"{self.employee.name} {self.employee.patronymic}, ОГРНИП: "
                f"{self.ogrnip}, ИНН: {self.employee.inn}, "
                f"{self.employee.address}, р/с {self.employee.checking_account}"
                f", {self.employee.bank}, БИК: {self.employee.bik}, к/с "
                f"{self.employee.correspondent_account}"
            )

    @property
    def display_name(self):
        """Admin site display name."""
        if self.is_active:
            return " ".join([str(self.number), self.employee.full_name])
        else:
            return " ".join([str(self.number), self.employee.full_name, "⛔️"])

    def __str__(self):
        return self.display_name


class SalaryCertificate(models.Model):
    """SalaryCertificate model."""

    class Meta:
        """SalaryCertificate metaclass."""

        verbose_name = "зарплатный акт"
        verbose_name_plural = "зарплатные акты"

    number = models.IntegerField("Номер документа", unique=True)
    start_date = models.DateField("Начало отчётного периода")
    end_date = models.DateField("Конец отчётного периода")
    original_signed = models.BooleanField("Оригинал подписан", default=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="salary_certificate",
        verbose_name="договор",
    )


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
