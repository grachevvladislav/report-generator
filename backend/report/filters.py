from core.models import Employee
from django.contrib import admin
from filters import DateFilter
from utils import first_day_of_the_previous_month


class EmployeeAccrualFilter(admin.SimpleListFilter):
    """Group accrual by Employee."""

    title = "Сотрудник"
    parameter_name = "employee"

    def lookups(self, request, model_admin):
        """Get list of options."""
        query = (
            Employee.objects.filter(
                accrual__isnull=False,
            )
            .distinct()
            .order_by("surname")
        )
        return ((i.id, i.short_name) for i in query)

    def queryset(self, request, queryset):
        """Get filtered queryset."""
        if self.value():
            return queryset.filter(employee=self.value())
        else:
            return queryset


class EmployeeSaleFilter(EmployeeAccrualFilter):
    """Group sale by Employee."""

    title = "Сотрудник"
    parameter_name = "employee"

    def lookups(self, request, model_admin):
        """Get list of options."""
        query = (
            Employee.objects.filter(
                sale__isnull=False,
            )
            .distinct()
            .order_by("surname")
        )
        return ((i.id, i.short_name) for i in query)


class DateReportFilter(DateFilter):
    """Group query by month. Default - previous month."""

    def choices(self, changelist):
        """Add default choice."""
        for lookup, title in self.lookup_choices:
            last_month = first_day_of_the_previous_month()
            yield {
                "selected": self.value() == str(lookup)
                or (
                    self.value() is None
                    and f"{last_month.year}-{last_month.month}" == str(lookup)
                ),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, []
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        """Get filtered queryset."""
        if self.value():
            year, month = map(int, self.value().split("-"))
            return queryset.filter(date__year=year, date__month=month)
        else:
            last_month = first_day_of_the_previous_month()
            return (
                queryset.filter(
                    date__year=last_month.year, date__month=last_month.month
                )
                or queryset
            )
