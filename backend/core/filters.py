import calendar

from django.contrib import admin
from django.db.models.functions import ExtractMonth, ExtractYear

from .models import Employee


class DateFilter(admin.SimpleListFilter):
    """Group schedule by month."""

    title = "Дата"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        """Get list of options."""
        query = (
            model_admin.get_queryset(request)
            .annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
            .values("year", "month")
            .distinct()
            .order_by("-year", "-month")
        )
        return (
            (
                f"{i['year']}-{i['month']}",
                f'{calendar.month_abbr[int(i["month"])].title()} {i["year"]}',
            )
            for i in query
        )

    def queryset(self, request, queryset):
        """Get filtered queryset."""
        if self.value():
            year, month = map(int, self.value().split("-"))
            return queryset.filter(date__year=year, date__month=month)
        else:
            return queryset


class EmployeeScheduleFiler(admin.SimpleListFilter):
    """Group schedule by Employee."""

    title = "Сотрудник"
    parameter_name = "employee"

    def lookups(self, request, model_admin):
        """Get list of options."""
        query = Employee.objects.filter(
            role__in=[Employee.Role.ADMIN, Employee.Role.OWNER],
        )
        return ((i.id, i.display_name) for i in query)

    def queryset(self, request, queryset):
        """Get filtered queryset."""
        if self.value():
            return queryset.filter(employee=self.value())
        else:
            return queryset