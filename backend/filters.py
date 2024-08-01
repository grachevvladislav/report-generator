import calendar
import datetime

from django.contrib import admin
from django.db.models.functions import ExtractMonth, ExtractYear


class DateFilter(admin.SimpleListFilter):
    """Group query by month."""

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

    def choices(self, changelist):
        """Add default choice."""
        for lookup, title in self.lookup_choices:
            today = datetime.date.today()
            yield {
                "selected": self.value() == str(lookup)
                or (
                    self.value() is None
                    and f"{today.year}-{today.month}" == str(lookup)
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
            today = datetime.date.today()
            return (
                queryset.filter(date__year=today.year, date__month=today.month)
                or queryset
            )
