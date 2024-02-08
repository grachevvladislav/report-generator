import datetime
import re
from calendar import monthrange

import dateutil

from config import settings
from constants.constants import data_button_pattern, months
from constants.exceptions import AdminFail, ParseFail
from constants.roles import Roles
from models import Employees, WorkingDay
from services import service
from utils import key_name_generator


def get_user_permissions() -> dict:
    table_raw = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.bot_settings_url.get_secret_value(),
            range="employees!A:N",
        )
        .execute()["values"]
    )
    constants = {
        "stuff_ids": [],
        "admins_dict": {},
    }
    for line in table_raw:
        if line[10] == Roles.STUFF.value and line[11] == "Да":
            constants["stuff_ids"].append(line[9])
        elif line[10] == Roles.ADMINISTRATOR.value and line[11] == "Да":
            constants["admins_dict"][line[9]] = line[0]
    return constants


def get_cashier_id() -> str:
    value = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.bot_settings_url.get_secret_value(),
            range="constants!G2",
        )
        .execute()["values"]
    )
    return value[0][0]


def get_settings_sheets() -> dict:
    tables_dict = {}
    tables_raw = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=settings.bot_settings_url.get_secret_value(),
            ranges=["document_counter!A1", "constants!A2:AA", "employees!A:N"],
        )
        .execute()["valueRanges"]
    )
    for table in tables_raw:
        tables_dict[table["range"].split("!")[0]] = table["values"]
    last_month = datetime.datetime.now()
    if not settings.debug:
        last_month += dateutil.relativedelta.relativedelta(months=-1)
    last_day_of_month = monthrange(last_month.year, last_month.month)[1]
    constants = {
        "default_working_time": float(tables_dict["constants"][0][0]),
        "percentage_of_sales": float(tables_dict["constants"][0][1]),
        "admin_by_hours": float(tables_dict["constants"][0][2]),
        "customer_details": tables_dict["constants"][0][3],
        "customer_short": tables_dict["constants"][0][4],
        "default_classes": [x[5] for x in tables_dict["constants"]],
        "document_counter": int(tables_dict["document_counter"][0][0]),
        "from": f"1.{last_month.strftime('%m.%Y')}г.",
        "to": f"{last_day_of_month}.{last_month.strftime('%m.%Y')}г.",
        "date": datetime.datetime.today().strftime("%d.%m.%Y"),
        "employees": tables_dict["employees"],
    }
    return constants


def get_employees_info(data: dict, mode: str) -> Employees:
    employees = Employees()
    keys = data[0]
    for line in data[1:]:
        if not len(line) == 12:
            raise ParseFail(f'Ошибка в строке\n{" ".join(line)}')
        if line[11] == "Нет" or mode != line[10]:
            continue
        employees.set_attribute(
            line[0], is_for_report=True, **dict(zip(keys, line[:11]))
        )
    return employees


def set_default_classes(employees, constants):
    for employee in employees.get_active_employee():
        employee.conducted_classes.update(
            dict.fromkeys(constants["default_classes"], 0)
        )


def get_admins_working_time(employees, constants):
    results = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.schedule_url.get_secret_value(),
            range=f"{constants['last_month'].year}!A2:I900",
        )
        .execute()
    )
    for day in results["values"]:
        if not len(day) > 1 or day[1] == "--":
            continue
        if key_name_generator(day[1]) not in employees.get_names():
            employees.add_notifications(
                f'Неизвестный сотрудник в расписании\n {" ".join(day)}'
            )
        try:
            day_date = datetime.datetime.strptime(day[0], "%d.%m.%Y")
        except ValueError:
            raise AdminFail(f'Ошибка в дате\n{" ".join(day)}')
        if (
            day_date.month == constants["last_month"].month
            and day_date.year == day_date.year
        ):
            if len(day) > 2:
                try:
                    time = float(day[2].replace(",", "."))
                except ValueError:
                    raise AdminFail(
                        f'Ошибка при указании времени\n {" ".join(day)}'
                    )
            else:
                time = constants["default_working_time"]
            employees.set_attribute(day[1].strip(), admin_work_time=time)


def get_admin_schedule(employee_name=None, data_range=None) -> (list, list):
    now_date = datetime.datetime.today()
    if data_range and re.match(r"^[0-9]{2}\.[0-9]{4}$", data_range):
        data_range = datetime.datetime.strptime(
            data_range, data_button_pattern
        )
    else:
        data_range = now_date
    raw_table = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.schedule_url.get_secret_value(),
            range=f"{data_range.year}!A2:B900",
        )
        .execute()
    )
    working_days = []
    for day in raw_table["values"]:
        if not len(day) > 1:
            continue
        try:
            db_date = datetime.datetime.strptime(day[0], "%d.%m.%Y")
        except ValueError:
            raise AdminFail(f'Ошибка в дате\n{" ".join(day)}')

        if db_date.month == data_range.month and (
            not employee_name or employee_name == day[1]
        ):
            new_day = WorkingDay(date=db_date, fio=day[1])

            if working_days and (
                (
                    working_days[-1].date + datetime.timedelta(days=1)
                    < new_day.date
                )
                or working_days[-1].fio != new_day.fio
            ):
                working_days.append(WorkingDay(delimiter=True))
            working_days.append(WorkingDay(date=db_date, fio=day[1]))

    message = f"Актуальный график на {months[data_range.month - 1]}:\n\n"
    for day in working_days:
        message += day.full_string(date=now_date, full=not bool(employee_name))
    up = data_range + dateutil.relativedelta.relativedelta(months=1)
    down = data_range + dateutil.relativedelta.relativedelta(months=-1)
    buttons = [
        ["<- " + months[down.month - 1], down.strftime(data_button_pattern)],
        [months[up.month - 1] + " ->", up.strftime(data_button_pattern)],
    ]
    return message, buttons


def update_document_counter(constants: dict) -> None:
    service.spreadsheets().values().update(
        spreadsheetId=settings.bot_settings_url.get_secret_value(),
        range="document_counter!A1",
        valueInputOption="USER_ENTERED",
        body={
            "majorDimension": "ROWS",
            "values": [[constants["document_counter"]]],
        },
    ).execute()
