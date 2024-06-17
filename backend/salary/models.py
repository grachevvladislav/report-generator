from decimal import Decimal

from core.models import Employee
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .exceptions import AlreadyExists


class SalaryCertificate(models.Model):
    """SalaryCertificate model."""

    class Meta:
        """SalaryCertificate metaclass."""

        verbose_name = "зарплатный акт"
        verbose_name_plural = "зарплатные акты"

    number = models.IntegerField("Номер документа", unique=True)
    start_date = models.DateField("Начало отчётного периода")
    end_date = models.DateField("Конец отчётного периода")


class Accrual(models.Model):
    """Accrual from FitBase."""

    class Meta:
        """Accrual metaclass."""

        verbose_name = "начисление"
        verbose_name_plural = "начисления"
        unique_together = ("date", "employee", "name", "base", "sum")

    date = models.DateTimeField("Дата начисления")
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="accrual",
        blank=True,
        null=True,
        default=None,
    )
    name = models.CharField("Название", blank=True, null=True)
    base = models.CharField("Основание", blank=True, null=True)
    sum = models.FloatField("Сумма")

    def __init__(self, *args, **kwargs):
        """Init method. Added correction for empty lines."""
        super().__init__(*args, **kwargs)
        for field in self._meta.get_fields():
            value = getattr(self, field.attname)
            if str(value) == "nan" or value == "-":
                setattr(self, field.attname, None)

    def __str__(self):
        return f'{self.date} {self.employee} {self.name or ""} {self.base or ""} {self.sum}'

    def clean(self):
        """Added check for the existence of a similar entry."""
        super().clean()
        if Accrual.objects.filter(
            date=self.date,
            employee__id=self.employee.id,
            name=self.name,
            base=self.base,
            sum=self.sum,
        ).exists():
            raise AlreadyExists("Запись уже существует")


class Sale(models.Model):
    """Sale from FitBase."""

    class Meta:
        """Sale metaclass."""

        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        unique_together = ("date", "employee", "name", "sum")

    date = models.DateTimeField("Дата оплаты")
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="sale",
        blank=True,
        null=True,
        default=None,
    )
    sum = models.FloatField("Сумма")
    name = models.CharField("Название", blank=True, null=True)


class Contract(models.Model):
    """Contract model."""

    class Meta:
        """Contract rule metaclass."""

        verbose_name = "договор"
        verbose_name_plural = "договоры"

    class Role(models.TextChoices):
        """Types of system role."""

        TRAINER = "Тренер", "Тренер"
        ADMIN = "Администратор", "Администратор"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="сontract"
    )

    is_active = models.BooleanField("Договор действует", default=True)
    role = models.CharField(choices=Role.choices, default=Role.TRAINER)
    tax_registration_date = models.DateField(
        "Дата регистрации в качестве плательщика НПД", blank=True, null=True
    )
    number = models.IntegerField("Номер договора", unique=True)
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


class Rule(models.Model):
    """Salary rule model."""

    class Meta:
        """Salary rule metaclass."""

        verbose_name = "правило"
        verbose_name_plural = "правила"

    class Type(models.TextChoices):
        """Types of salary rule."""

        RATE = "Ставка", "Ставка"
        ACCRUAL_AMOUNT = "Сумма начислений", "Сумма начислений"
        PERCENTAGE_OF_SALAS = (
            "Процент от личных продаж",
            "Процент от личных продаж",
        )
        HOURLY_PAYMENT = "Почасовая оплата", "Почасовая оплата"

    type = models.CharField(choices=Type.choices, default=Type.RATE)
    name = models.CharField("Название")
    rate_value = models.FloatField("Сумма")
    required_fields = ArrayField(models.CharField(), blank=True, null=True)
    percentage_value = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal(0),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="rule",
    )

    def __str__(self):
        return " ".join([self.type, self.name])
