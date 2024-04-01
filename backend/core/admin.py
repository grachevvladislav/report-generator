from django.contrib import admin, messages

from .filters import DateFilter
from .models import ActivitieType, Default, Employee, Schedule


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


class ScheduleAdmin(admin.ModelAdmin):
    """ScheduleAdmin admin site."""

    actions = ("set_default_time",)

    @admin.action(description="Установить рабочее время по умолчанию")
    def set_default_time(modeladmin, request, queryset):
        """Set worktime from defaults."""
        defaults = Default.objects.first()
        if not defaults:
            messages.error(request, "Время по умолчанию не указано!")
        else:
            for obj in queryset:
                obj.time = defaults.work_time
                obj.save()
            messages.success(request, "Успех!")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only administrators can be on the schedule."""
        kwargs["queryset"] = Employee.objects.filter(
            role__in=[Employee.Role.ADMIN, Employee.Role.OWNER]
        )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_filter = (DateFilter,)

    list_display = ("date", "employee", "time")


admin.site.register(ActivitieType, ActivitieTypeAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Default, DefaultAdmin)
admin.site.register(Schedule, ScheduleAdmin)
