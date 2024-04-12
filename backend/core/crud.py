import datetime
import io

import openpyxl
from django.apps import apps
from django.db.models.fields.related import ForeignKey

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
    wb = openpyxl.Workbook()
    buffer = io.BytesIO()
    models = apps.get_app_config("core").get_models()
    for model in models:
        ws = wb.create_sheet(model.__name__)
        fields = [field.name for field in model._meta.fields]
        ws.append(fields)
        for obj in model.objects.all():
            line = []
            for field in model._meta.fields:
                value = getattr(obj, field.name)
                if value and isinstance(field, ForeignKey):
                    line.append(value.id)
                else:
                    line.append(value)
            ws.append(line)
    wb.remove_sheet(wb.worksheets[0])
    wb.save(buffer)
    buffer.seek(0)
    return buffer
