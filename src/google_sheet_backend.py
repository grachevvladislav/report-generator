import datetime

import dateutil

from config import settings
from constants.exceptions import AdminFail, ParseFail
from constants.roles import Roles
from models import Employees
from services import service
from utils import key_name_generator


def get_user_permissions() -> dict:
    tables_raw = (
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
    for line in tables_raw:
        if line[10] == Roles.STUFF.value:
            constants["stuff_ids"].append(line[9])
        elif line[10] == Roles.ADMINISTRATOR.value:
            constants["admins_dict"][line[9]] = line[0]
    return constants


def get_settings_sheets() -> dict:
    tables_dict = {}
    tables_raw = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=settings.bot_settings_url.get_secret_value(),
            ranges=["document_counter!A1", "constants!A2:G", "employees!A:N"],
        )
        .execute()["valueRanges"]
    )
    for table in tables_raw:
        tables_dict[table["range"].split("!")[0]] = table["values"]
    last_month = datetime.datetime.now()
    if not settings.debug:
        last_month += dateutil.relativedelta.relativedelta(months=-1)
    constants = {
        "default_working_time": float(tables_dict["constants"][0][0]),
        "percentage_of_sales": float(tables_dict["constants"][0][1]),
        "admin_by_hours": float(tables_dict["constants"][0][2]),
        "trainer_by_hours": float(tables_dict["constants"][0][3]),
        "customer_details": tables_dict["constants"][0][4],
        "customer_short": tables_dict["constants"][0][5],
        "default_classes": [x[6] for x in tables_dict["constants"]],
        "document_counter": int(tables_dict["document_counter"][0][0]),
        "last_month": last_month,
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
            employees.add_notification(
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


def get_admin_schedule(client_name, data_range=None) -> (list, list):
    now_date = datetime.datetime.now()
    if data_range:
        data_range = datetime.datetime.strptime(data_range, "%m.%Y")
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
    result = [f"Рабочий график на {data_range.month}:"]
    delimiter = "---"
    for day in raw_table["values"]:
        if not len(day) > 1 or day[1] == "--":
            continue
        try:
            db_date = datetime.datetime.strptime(day[0], "%d.%m.%Y")
        except ValueError:
            raise AdminFail(f'Ошибка в дате\n{" ".join(day)}')
        if client_name == day[1] and db_date.month == data_range.month:
            if now_date > db_date:
                line = "✅ "
            else:
                line = "☑️ "
            line += db_date.strftime("%d %B")
            result.append(line)
        elif not result[-1] == delimiter:
            result.append(delimiter)
    up = data_range + dateutil.relativedelta.relativedelta(months=1)
    down = data_range + dateutil.relativedelta.relativedelta(months=-1)
    buttons = [
        [down.strftime("<- %B"), down.strftime("%m.%Y")],
        [up.strftime("%B ->"), up.strftime("%m.%Y")],
    ]
    return result, buttons


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
