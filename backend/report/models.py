from core.models import Employee
from django.db import models
from exceptions import AlreadyExists


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
        return " ".join(
            filter(
                None,
                map(
                    str,
                    [self.date, self.employee, self.name, self.base, self.sum],
                ),
            )
        )

    def clean(self):
        """Added check for the existence of a similar entry."""
        super().clean()
        if Accrual.objects.filter(
            date=self.date,
            employee__id=getattr(self.employee, "id", None),
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
        unique_together = ("date", "employee", "name", "sum", "client")

    date = models.DateTimeField("Дата оплаты")
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="sale",
        blank=True,
        null=True,
        default=None,
    )
    client = models.CharField("Клиент", blank=True, null=True, default=None)
    sum = models.FloatField("Сумма")
    name = models.CharField("Название", blank=True, null=True)

    def __str__(self):
        return " ".join(
            filter(
                None,
                [self.date, self.employee, self.name, self.client, self.sum],
            )
        )
