import datetime
import io

from borb.pdf import PDF, Document
from django.core import management

from .make_pdf import create_list
from .models import Default, Employee, Schedule
from .utils import append_data


async def get_missing_dates(enable_empty):
    start_date = datetime.datetime.now().date()
    db = await Schedule.objects.afilter(
        date__range=[
            start_date,
            append_data(
                start_date, days=Default.get_default("planning_horizon")
            ),
        ]
    )
    if enable_empty:
        db = await db.afilter(employee__isnull=False)
    db = await db.values_list("date", flat=True).distinct()
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


def create_pdf(employees: list[Employee], constants: dict) -> io.BytesIO:
    doc = Document()
    for employee in employees.get_active_employee():
        constants["document_counter"] += 1
        employee_dict = employee.to_dict()
        employee_dict.update(constants)
        page = create_list(employee_dict)
        doc.add_page(page)

    memory_file = io.BytesIO()
    PDF.dumps(memory_file, doc)
    memory_file.seek(0)
    return memory_file
