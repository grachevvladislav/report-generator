import datetime

from config import settings
from exceptions import ParseFail
from services import service
from utils import name_shortener

keys = [
    "fio",
    "inn",
    "address",
    "checking_account",
    "bank",
    "bik",
    "correspondent_account",
    "agreement_number",
    "agreement_date",
    "role",
    "work_time",
    "kpi_money",
]


def get_settings_sheets():
    sheets = {}
    data = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=settings.bot_settings_url.get_secret_value(),
            ranges=[
                "admins!A1:A100",
                "document_counter!A1",
                "employees!A2:K900",
                "constants!B1:B100",
            ],
        )
        .execute()["valueRanges"]
    )
    for table in data:
        sheets[table["range"].split("!")[0]] = table["values"]
    return sheets


def get_employees(data: list[list[str]]) -> dict:
    employees = {}
    for employee in data:
        if not len(employee) == 11:
            raise ParseFail(f'Ошибка в строке\n{" ".join(employee)}')
        if employee[10] == "Нет":
            continue
        employees[name_shortener(employee[0])] = {}
        for key, value in zip(keys[:10], employee[:10]):
            employees[name_shortener(employee[0])][key] = value
        for key in keys[10:]:
            employees[name_shortener(employee[0])][key] = 0
    return employees


def get_constants(settings_sheets: dict) -> dict:
    constants = {
        "default_working_time": float(settings_sheets["constants"][0][0]),
        "percentage_of_sales": float(settings_sheets["constants"][1][0]),
        "admin_by_hours": float(settings_sheets["constants"][2][0]),
        "trainer_by_hours": float(settings_sheets["constants"][3][0]),
        "document_counter": int(settings_sheets["document_counter"][0][0]),
        "stuff_ids": [int(x[0]) for x in settings_sheets["admins"]],
        "customer_details": settings_sheets["constants"][4][0],
        "customer_short": settings_sheets["constants"][5][0],
    }
    return constants


def get_admins_working_time(employees, period, constants):
    results = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.schedule_url.get_secret_value(),
            range=f"{period.year}!A2:I900",
        )
        .execute()
    )
    for day in results["values"]:
        if not len(day) > 1 or day[1] == "--":
            continue
        try:
            day_date = datetime.datetime.strptime(day[0], "%d.%m.%Y")
        except ValueError:
            raise ParseFail(f'Ошибка в дате\n{" ".join(day)}')
        if day_date.month == period.month and day_date.year == day_date.year:
            if len(day) > 2:
                try:
                    time = float(day[2].replace(",", "."))
                except ValueError:
                    raise ParseFail(
                        f'Ошибка при указании времени\n {" ".join(day)}'
                    )
            else:
                time = constants["default_working_time"]
            employees[name_shortener(day[1])]["work_time"] += time


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
