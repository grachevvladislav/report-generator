import calendar

from django.contrib import admin
from django.db.models.functions import ExtractMonth, ExtractYear
from utils import first_day_of_the_previous_month


class SalaryCertificateDateFilter(admin.SimpleListFilter):
    """Group Salary Certificate by start date month."""

    title = "Дата"
    parameter_name = "month"

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
            last_month = first_day_of_the_previous_month()
            return (
                queryset.filter(
                    start_date__year=last_month.year,
                    start_date__month=last_month.month,
                )
                or queryset
            )
