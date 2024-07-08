import datetime
from decimal import Decimal

from core.models import Employee, Schedule
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Concat
from report.models import Accrual, Sale
from utils import (
    first_day_of_the_previous_month,
    last_day_of_the_previous_month,
)

from constants import date_pattern


class Table:
    """Document table."""

    def __init__(self):
        """Init class."""
        self.lines = []
        self.lines_counter = 0
        self.full_sum = 0

    def add_line(
        self, full_name: str, count: float | int, unit: str, sum: float | int
    ):
        """Add new record in table."""
        self.full_sum += count * sum
        self.lines_counter += 1
        self.lines.append(
            map(
                str,
                [
                    self.lines_counter,
                    full_name,
                    count,
                    unit,
                    "{0:.2f}".format(sum),
                    "{0:.2f}".format(count * sum),
                ],
            )
        )

    def as_dict(self):
        """Get data for doc creation function."""
        return {
            "table": self.lines,
            "sum": "{0:.2f}".format(self.full_sum),
        }


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

    def admin_name(self):
        """Admin site display name."""
        value = f"#{self.number} {self.employee.full_name} {self.template}"
        if not self.is_active:
            return value + " ⛔"
        if self.original_signed:
            return value
        return value + " ❗️"

    def __str__(self):
        return self.admin_name()


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

    def clean(self):
        """Validate start and end dates. Elimination of intersections."""
        super().clean()
        errors = {}
        if self.contract_id is None:
            raise ValidationError(errors)
        if self.end_date and self.start_date > self.end_date:
            errors["start_date"] = "Дата начала не может быть позже конца!"
        if self.start_date < self.contract.start_date:
            errors["start_date"] = (
                f"Не может быть раньше подписания договора \n"
                f"{self.contract.start_date.strftime(date_pattern)}"
            )
        if self.contract.end_date and self.end_date > self.contract.end_date:
            errors["end_date"] = (
                f"Не может быть позже расторжения договора "
                f"{self.contract.end_date.strftime(date_pattern)}"
            )
        start_overlap = (
            SalaryCertificate.objects.filter(
                contract=self.contract,
                end_date__gte=self.start_date,
                start_date__lte=self.start_date,
            )
            .exclude(id=self.id)
            .first()
        )
        if start_overlap:
            errors["start_date"] = (
                f"Последний акт закончился "
                f"{start_overlap.end_date.strftime(date_pattern)}!"
            )
        end_overlap = (
            SalaryCertificate.objects.filter(
                contract=self.contract,
                end_date__gte=self.end_date,
                start_date__lte=self.end_date,
            )
            .exclude(id=self.id)
            .first()
        )
        if end_overlap:
            errors["end_date"] = (
                f"Следующий акт начался "
                f"{end_overlap.end_date.strftime(date_pattern)}!"
            )
        if errors:
            raise ValidationError(errors)

    def get_data(self):
        """Get table data for doc."""
        table = Table()
        # Accrual data
        # Need to add date filter
        required_fields = AmountOfAccrual.objects.filter(
            contract=self.contract.template
        )
        if required_fields:
            query = (
                Accrual.objects.filter(
                    employee=self.contract.employee,
                    date__date__range=[self.start_date, self.end_date],
                )
                .values("employee")
                .annotate(
                    full_name=models.Case(
                        models.When(name=None, then=models.F("base")),
                        models.When(base=None, then=models.F("name")),
                        default=Concat("name", models.Value(" "), "base"),
                        output_field=models.CharField(),
                    ),
                    count=models.Count("sum"),
                    result=models.Sum("sum"),
                )
                .values("full_name", "count", "sum", "result")
            )
            # add check required fields in set
            compile_required = {
                (i.required_field, i.value): False for i in required_fields
            }
            for line in query:
                if (line["full_name"], line["sum"]) in compile_required.keys():
                    compile_required[(line["full_name"], line["sum"])] = True
                table.add_line(
                    full_name=line["full_name"],
                    count=line["count"],
                    unit="шт.",
                    sum=line["sum"],
                )
            for field, is_add in compile_required.items():
                if not is_add:
                    table.add_line(
                        full_name=field[0],
                        count=0,
                        unit="шт.",
                        sum=field[1],
                    )
        # RATE data
        # NEED TO EDIT
        rates = Rate.objects.filter(contract=self.contract.template)
        if rates:
            for rate in rates:
                table.add_line(
                    full_name=rate.name, count=1, unit="шт.", sum=rate.value
                )
        # PercentageOfSales date
        percent = PercentageOfSales.objects.filter(
            contract=self.contract.template
        ).first()
        if percent:
            query = (
                Sale.objects.filter(
                    employee=self.contract.employee,
                    date__date__range=[self.start_date, self.end_date],
                )
                .values("employee")
                .annotate(
                    result=models.Sum("sum"),
                )
                .values_list("result", flat=True)
            )
            table.add_line(
                full_name=percent.name,
                count=1,
                unit="шт.",
                sum=query[0] * float(percent.percentage_value) / 100,
            )
        # HourlyPayment
        payment = HourlyPayment.objects.filter(
            contract=self.contract.template
        ).first()
        if payment:
            query = (
                Schedule.objects.filter(
                    employee=self.contract.employee,
                    date__range=[self.start_date, self.end_date],
                )
                .values("employee")
                .annotate(
                    result=models.Sum("time"),
                )
                .values_list("result", flat=True)
            )
            table.add_line(
                full_name=payment.name,
                count=query[0],
                unit="ч.",
                sum=payment.value,
            )
        return table.as_dict()

    def admin_name(self):
        """Name for first field in admin."""
        value = f"#{self.number} от {self.date_of_creation}"
        if self.original_signed:
            return value
        return value + " ❗️"

    admin_name.short_description = "Номер"

    def admin_sum(self):
        """Total amount."""
        return "{0:,.2f} р.".format(Decimal(self.get_data()["sum"])).replace(
            ",", " "
        )

    def __str__(self):
        value = (
            f"#{self.number} от "
            f"{self.date_of_creation.strftime(date_pattern)} "
            f"{self.contract.template} {self.contract.employee.full_name}"
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
    value = models.FloatField(
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
    value = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )
    contract = models.ForeignKey(
        ContractTemplate,
        on_delete=models.CASCADE,
        related_name="amount_of_accrual",
    )

    def __str__(self):
        return " ".join(map(str, [self.required_field, self.value]))


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
        unique=True,
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
    value = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )
    contract = models.OneToOneField(
        ContractTemplate,
        on_delete=models.CASCADE,
        unique=True,
        related_name="hourly_payment",
    )

    def __str__(self):
        return " ".join(map(str, [self.name, self.value]))
