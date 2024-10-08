import datetime
from decimal import Decimal

from constants import date_pattern
from core.models import Employee, Schedule
from django.core.exceptions import FieldError, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Concat
from report.models import Accrual, Sale
from utils import (
    first_day_of_the_previous_month,
    format_money,
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

    def is_active(self):
        """Return current status of the contract."""
        if self.end_date:
            return datetime.date.today() <= self.end_date
        return True

    is_active.boolean = True
    is_active.short_description = "Действует"

    def admin_name(self):
        """Admin site display name."""
        value = f"#{self.number} {self.employee.full_name()} {self.template}"
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
    is_blocked = models.BooleanField(
        "Редактирование не доступно", default=False
    )
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
                f"Следующий акт закончился "
                f"{end_overlap.end_date.strftime(date_pattern)}!"
            )
        if errors:
            raise ValidationError(errors)

    def calculate(self):
        """Calculate by template rules."""
        if self.is_blocked:
            raise FieldError("Заблокирован от изменений")
        if self.original_signed:
            raise FieldError("Оригинал уже подписан")
        Field.objects.filter(
            salary_certificate_id=self.id,
            is_auto=True,
        ).delete()
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
                )
                .values("full_name", "count", "sum")
            )
            # add check required fields in set
            compile_required = set(
                ((i.required_field, i.value) for i in required_fields)
            )
            for line in query:
                if (line["full_name"], line["sum"]) in compile_required:
                    compile_required.remove((line["full_name"], line["sum"]))
                Field.objects.get_or_create(
                    salary_certificate_id=self.id,
                    name=line["full_name"],
                    price=line["sum"],
                    count=line["count"],
                    is_auto=True,
                )
            for name, price in compile_required:
                Field.objects.get_or_create(
                    salary_certificate_id=self.id,
                    name=name,
                    price=price,
                    is_auto=True,
                )
        # RATE data
        # NEED TO EDIT
        rates = Rate.objects.filter(contract=self.contract.template)
        if rates:
            for rate in rates:
                Field.objects.get_or_create(
                    salary_certificate_id=self.id,
                    name=rate.name,
                    count=1,
                    price=rate.value,
                    is_auto=True,
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
            if query:
                summ = query[0] * float(percent.percentage_value) / 100
            else:
                summ = 0
            Field.objects.get_or_create(
                salary_certificate_id=self.id,
                name=percent.name,
                count=1,
                price=summ,
                is_auto=True,
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
            Field.objects.get_or_create(
                salary_certificate_id=self.id,
                name=payment.name,
                count=query[0],
                price=payment.value,
                is_auto=True,
            )

    def get_data(self):
        """Get table data for doc."""
        return Field.objects.filter(
            salary_certificate_id=self.id,
        )

    def get_sum(self):
        """Total amount."""
        summ = (
            Field.objects.filter(salary_certificate_id=self.id)
            .annotate(sum=models.F("price") * models.F("count"))
            .aggregate(full_sum=models.Sum("sum"))["full_sum"]
            or 0
        )
        return format_money(summ)

    get_sum.short_description = "Сумма"

    def admin_name(self):
        """Name for first field in admin."""
        value = f"#{self.number} от {self.date_of_creation}"
        if not self.original_signed:
            value += " ❗️"
        if not self.is_blocked:
            value += " 🔓"
        return value

    admin_name.short_description = "Номер"

    def __str__(self):
        value = (
            f"#{self.number} от "
            f"{self.date_of_creation.strftime(date_pattern)} "
            f"{self.contract.employee.full_name()}"
        )
        if not self.original_signed:
            value += " ❗️"
        value += f" {self.get_sum()}"
        return value


class Field(models.Model):
    """Salary certificate table fields."""

    class Meta:
        """Rate metaclass."""

        verbose_name = "Строка"
        verbose_name_plural = "Строки"
        unique_together = ("name", "salary_certificate", "is_auto")

    name = models.CharField(
        "Название",
    )
    price = models.FloatField(
        "Цена",
    )
    count = models.FloatField("Колл-во", default=0)
    unit = models.CharField("Ед.", default="шт.")

    is_auto = models.BooleanField("Автоматическое поле", default=False)
    salary_certificate = models.ForeignKey(
        SalaryCertificate, on_delete=models.CASCADE, related_name="field"
    )

    def __str__(self):
        return f"{self.name} {self.price} x {self.count} = {self.summ()}р."

    def summ(self):
        """Summ."""
        return self.count * self.price


class Rate(models.Model):
    """Rate rule for ContractTemplate."""

    class Meta:
        """Rate metaclass."""

        verbose_name = "ставка"
        verbose_name_plural = "Правило: Ставка"
        unique_together = (
            "name",
            "contract",
        )

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
