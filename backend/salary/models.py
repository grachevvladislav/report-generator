from core.models import Employee
from django.db import models


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

    date = models.DateField("Дата начисления")
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
    sum = models.FloatField("Сумма", blank=True, null=True)
