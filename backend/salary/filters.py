import calendar

from django.contrib import admin
from django.db.models.functions import ExtractMonth, ExtractYear


class SalaryCertificateDateFilter(admin.SimpleListFilter):
    """Group Salary Certificate by start date month."""

    title = "Дата"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        """Get list of options."""
        query = (
            model_admin.get_queryset(request)
            .annotate(
                year=ExtractYear("start_date"),
                month=ExtractMonth("start_date"),
            )
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
            return queryset.filter(
                start_date__year=year, start_date__month=month
            )
        else:
            return queryset
