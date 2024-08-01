from django.contrib import admin

from .models import Employee


class EmployeeScheduleFilter(admin.SimpleListFilter):
    """Group schedule by Employee."""

    title = "Сотрудник"
    parameter_name = "employee"

    def lookups(self, request, model_admin):
        """Get list of options."""
        query = Employee.objects.filter(
            сontract__template__hourly_payment__isnull=False,
        ).distinct()
        return ((i.id, i.short_name) for i in query)

    def queryset(self, request, queryset):
        """Get filtered queryset."""
        if self.value():
            return queryset.filter(employee=self.value())
        else:
            return queryset
