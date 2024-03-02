from django.contrib import admin

from .models import ActivitieType, Default, Employee


class EmployeeAdmin(admin.ModelAdmin):
    """Employee admin site."""

    list_display = (
        "full_name",
        "tax_regime",
        "is_active",
        "is_approved",
        "role",
    )
    search_fields = ("tax_regime",)
    list_filter = ("is_active", "is_approved", "role")


class ActivitieTypeAdmin(admin.ModelAdmin):
    """ActivitieType admin site."""

    list_display = (
        "full_name",
        "duration_in_hours",
        "salary",
    )
    search_fields = ("full_name",)
    list_filter = ("salary",)


class DefaultAdmin(admin.ModelAdmin):
    """DefaultAdmin admin site."""

    list_display = (
        "work_time",
        "sale_kpi",
        "hourly_rate",
    )


admin.site.register(ActivitieType, ActivitieTypeAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Default, DefaultAdmin)
