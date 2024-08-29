import datetime
import io

from asgiref.sync import sync_to_async
from constants import months
from django.core import management
from utils import append_data

from .models import Default, Employee, Schedule


def export_all_tables():
    buffer = io.StringIO()
    management.call_command(
        "dumpdata",
        "--exclude",
        "auth.permission",
        "--exclude",
        "contenttypes",
        stdout=buffer,
    )
    buffer.seek(0)
    return buffer


def get_schedule_notifications():
    """Get empty date in schedule."""
    planning_horizon = Default.get_default("planning_horizon")
    if not planning_horizon:
        return []
    start_date = datetime.datetime.now().date()
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
    if not difference:
        return []
    grouped_dates = []
    current_group = [difference[0]]
    for i in range(1, len(difference)):
        if (difference[i] - difference[i - 1]).days == 1:
            current_group.append(difference[i])
        else:
            grouped_dates.append(current_group)
            current_group = [difference[i]]
    grouped_dates.append(current_group)
    msgs = []
    for group in grouped_dates:
        if len(group) == 1:
            text = f"Не назначен сотрудник на {group[0].strftime('%d %B')}"
        else:
            text = f"Не назначен сотрудник c {group[0].strftime('%d %B')} по {group[-1].strftime('%d %B')}"
        msgs.append(text)
    return msgs


async def get_schedule(
    data_range: datetime.datetime, employee: Employee = None
) -> str:
    now_date = datetime.datetime.now()
    message = (
        f"Актуальный график на {months[data_range.month - 1].lower()} {data_range.strftime('%Y')}г.\n"
        f"Обновлено "
        f"{now_date.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
    )
    if employee:
        working_days = await sync_to_async(
            Schedule.objects.filter(
                date__month=data_range.month,
                date__year=data_range.year,
                employee=employee,
            ).order_by
        )("date")
    else:
        notifications = [
            "❗️" + line
            for line in await sync_to_async(get_schedule_notifications)()
        ]
        message += "\n".join(notifications) + "\n\n"
        working_days = await sync_to_async(
            Schedule.objects.filter(
                date__month=data_range.month,
                date__year=data_range.year,
                employee__isnull=False,
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
        message += await sync_to_async(day.full_string_bot)(full=not employee)
        message += "\n"
    if not previous:
        message += "Пока нет расписания на выбранный период"
    return message
