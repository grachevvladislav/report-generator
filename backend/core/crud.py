import datetime
import io

from django.core import management

from .models import Default, Schedule
from .utils import append_data


def get_missing_dates(enable_empty):
    start_date = datetime.datetime.now().date()
    db = Schedule.objects.filter(
        date__range=[
            start_date,
            append_data(
                start_date, days=Default.get_default("planning_horizon")
            ),
        ]
    )
    if enable_empty:
        db = db.filter(employee__isnull=False)
    db = db.values_list("date", flat=True).distinct()
    if len(db) < Default.get_default("planning_horizon"):
        all_days = [
            append_data(start_date, days=date)
            for date in range(Default.get_default("planning_horizon"))
        ]
        difference = list(set(all_days) - set(db))
        difference.sort()
        return difference
    return []


def export_all_tables():
    buffer = io.StringIO()
    management.call_command("dumpdata", stdout=buffer)
    buffer.seek(0)
    return buffer
