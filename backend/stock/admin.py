from django.contrib import admin

from .models import Delivery, ItemDelivery, ItemWriteOff, Product, WriteOff


class ProductAdmin(admin.ModelAdmin):
    """ProductAdmin admin site."""

    list_display = ("name", "description", "admin_balance", "enough")
    search_fields = (
        "name",
        "description",
    )


class ItemDeliveryInLine(admin.TabularInline):
    """Inline add ItemDelivery."""

    model = ItemDelivery
    extra = 0


class DeliveryAdmin(admin.ModelAdmin):
    """DeliveryAdmin admin site."""

    list_display = ("name", "date", "admin_product_list", "is_shipped")
    search_fields = ("name",)
    inlines = (ItemDeliveryInLine,)


class ItemWriteOffInLine(admin.TabularInline):
    """Inline add ItemWriteOff."""

    model = ItemWriteOff
    extra = 0


class WriteOffAdmin(admin.ModelAdmin):
    """WriteOffAdmin admin site."""

    list_display = ("date", "admin_product_list")
    inlines = (ItemWriteOffInLine,)


admin.site.register(Product, ProductAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(WriteOff, WriteOffAdmin)
