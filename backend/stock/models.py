import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """Product model."""

    class Meta:
        """Product metaclass."""

        verbose_name = "товар"
        verbose_name_plural = "товары 📦"
        unique_together = ("name", "description")

    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.CharField(
        verbose_name="Описание", blank=True, null=True
    )
    units = models.CharField(verbose_name="Единица измерения", default="шт")

    def balance(self, exclude_id=None):
        """Return current balance."""
        delivered = (
            ItemDelivery.objects.filter(product=self).aggregate(
                sum=models.Sum("quantity")
            )["sum"]
            or 0
        )
        written_off = (
            ItemWriteOff.objects.filter(product=self)
            .exclude(id=exclude_id)
            .aggregate(sum=models.Sum("quantity"))["sum"]
            or 0
        )
        return delivered - written_off

    def admin_balance(self):
        """Return current balance with units."""
        return f"{self.balance()} {self.units}"

    admin_balance.short_description = "Текущий остаток"

    def __str__(self):
        return self.name


class BaseOrder(models.Model):
    """Abstract order class."""

    class Meta:
        """BaseItem metaclass."""

        abstract = True

    date = models.DateTimeField(
        "Дата создания", default=datetime.datetime.today, unique=True
    )

    def __str__(self):
        return self.date.strftime("%d.%m.%Y %H:%M:%S")


class Delivery(BaseOrder):
    """Delivery model."""

    class Meta:
        """Delivery metaclass."""

        verbose_name = "поставка"
        verbose_name_plural = "поставки ⬆️"

    name = models.CharField(max_length=200, verbose_name="Название")

    def admin_product_list(self):
        """List of products."""
        return ", ".join(
            ItemDelivery.objects.filter(delivery=self).values_list(
                "product__name", flat=True
            )
        )

    admin_product_list.short_description = "Список товаров"


class WriteOff(BaseOrder):
    """WriteOff model."""

    class Meta:
        """WriteOff metaclass."""

        verbose_name = "списание"
        verbose_name_plural = "списания ⬇️"

    def admin_product_list(self):
        """List of products."""
        return ", ".join(
            ItemWriteOff.objects.filter(write_off=self).values_list(
                "product__name", flat=True
            )
        )

    admin_product_list.short_description = "Список товаров"


class BaseItem(models.Model):
    """Abstract item class."""

    class Meta:
        """BaseItem metaclass."""

        abstract = True

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="%(class)s_item",
        default=None,
        verbose_name="товар",
    )

    def __str__(self):
        return " ".join(
            [
                self.product.__str__(),
                str(self.quantity),
                str(self.product.units),
            ]
        )


class ItemDelivery(BaseItem):
    """Item for delivery."""

    class Meta:
        """ItemDelivery metaclass."""

        verbose_name = "строка"
        verbose_name_plural = "строки"
        unique_together = (
            "delivery",
            "product",
        )

    quantity = models.IntegerField(
        verbose_name="Количество", validators=(MinValueValidator(0),)
    )
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name="item_delivery",
        default=None,
        verbose_name="товар",
    )


class ItemWriteOff(BaseItem):
    """Item for WriteOff."""

    class Meta:
        """WriteOff metaclass."""

        verbose_name = "строка"
        verbose_name_plural = "строки"
        unique_together = (
            "write_off",
            "product",
        )

    quantity = models.IntegerField(
        verbose_name="Количество",
    )
    write_off = models.ForeignKey(
        WriteOff,
        on_delete=models.CASCADE,
        related_name="item_write_off",
        default=None,
        verbose_name="товар",
    )

    def clean(self):
        """Clean data."""
        if self.quantity > self.product.balance(self.id):
            raise ValidationError(
                f"Нельзя списать больше {self.product.admin_balance()}!"
            )
