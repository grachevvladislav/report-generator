from core.models import Employee
from django.db import models

from .exceptions import AlreadyExists


class ActivitieType(models.Model):
    """ActivitieType model."""

    class Meta:
        """ActivitieType metaclass."""

        verbose_name = "правило"
        verbose_name_plural = "правила"

    name = models.CharField("Начисление", blank=True, null=True, unique=True)
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


class Document(models.Model):
    """Document model."""

    class Meta:
        """Document metaclass."""

        verbose_name = "акт"
        verbose_name_plural = "акты"

    number = models.IntegerField("Номер документа", unique=True)
    start_date = models.DateField("Начало отчётного периода")
    end_date = models.DateField("Конец отчётного периода")
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="document"
    )


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
