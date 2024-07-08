import datetime
import io

from asgiref.sync import sync_to_async
from django.core import management
from utils import append_data

from .models import Default, Employee, Schedule


def get_missing_dates(add_empty):
    start_date = datetime.datetime.now().date()
    planning_horizon = Default.get_default("planning_horizon")
    if not planning_horizon:
        return []
    if add_empty:
        db_set = (
            Schedule.objects.filter(
                date__range=[
                    start_date,
                    append_data(start_date, days=planning_horizon),
                ],
            )
            .values_list("date", flat=True)
            .distinct()
        )
    else:
        db_set = (
            Schedule.objects.filter(
                date__range=[
                    start_date,
                    append_data(start_date, days=planning_horizon),
                ],
                employee__isnull=False,
            )
            .values_list("date", flat=True)
            .distinct()
        )
    all_days = [
        append_data(start_date, days=date) for date in range(planning_horizon)
    ]
    difference = list(set(all_days) - set(db_set))
    difference.sort()
    return difference


def export_all_tables():
    buffer = io.StringIO()
    management.call_command("dumpdata", stdout=buffer)
    buffer.seek(0)
    return buffer


async def get_schedule(
    data_range: datetime.datetime, employee: Employee = None
) -> str:
    now_date = datetime.datetime.now()
    message = (
        f"Актуальный график на {now_date.strftime('%b %Y')}.\n"
        f"Обновлено "
        f"{now_date.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
    )
    if employee:
        working_days = await sync_to_async(Schedule.objects.filter)(
            date__month=data_range.month, employee=employee
        )
    else:
        working_days = await sync_to_async(
            Schedule.objects.filter(
                date__month=data_range.month, employee__isnull=False
            ).order_by
        )("date")
    previous = None
    async for day in working_days:
        if previous and (
            previous.employee_id != day.employee_id
            or append_data(previous.date, days=1) != day.date
        ):
            message += "------------\n"
        previous = day
        message += await sync_to_async(day.full_string)(full=not employee)
        message += "\n"
    if not previous:
        message += "Пока нет расписания на выбранный период"
    return message
