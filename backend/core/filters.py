import calendar

from django.contrib import admin
from django.db.models.functions import ExtractMonth, ExtractYear


class DateFilter(admin.SimpleListFilter):
    """Group schedule by month."""

    title = "Дата"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        """Get list of options."""
        tmp = (
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
            for i in tmp
        )

    def queryset(self, request, queryset):
        """Get filtered queryset."""
        if self.value():
            year, month = map(int, self.value().split("-"))
            return queryset.filter(date__year=year, date__month=month)
        else:
            return queryset
