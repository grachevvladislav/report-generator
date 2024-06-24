from datetime import datetime

import pandas as pd
from asgiref.sync import async_to_sync
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from exceptions import AlreadyExists, ParseFail
from pandas._typing import ReadCsvBuffer
from report.models import Accrual
from salary.crud import get_employee_by_name

sale_fields = ["Оплачено,\xa0₽", "Инициатор", "Наименование", "Дата оплаты"]
trainer_fields = [
    "Сумма",
    "Автодействие",
    "Комментарий",
    "Сотрудник",
    "Дата начисления",
]

date_format = "%d.%m.%Y %H:%M"


def trainer_report_parsing(file: ReadCsvBuffer) -> list[Accrual]:
    data = pd.read_csv(file).to_dict("records")
    if not all(key in data[0].keys() for key in trainer_fields):
        raise ParseFail("Неизвестный вид отчета. Нет обязательных полей.")
    accruals = []
    errors = []
    for n, line in zip(range(1, len(data) + 1), data):
        try:
            sum, name, base, person, date = [
                line[field] for field in trainer_fields
            ]
            employee = async_to_sync(get_employee_by_name)(person)
            line = Accrual(
                employee=employee,
                sum=sum,
                name=name,
                date=datetime.strptime(date, date_format),
                base=base,
            )
            line.full_clean()
        except AlreadyExists:
            continue
        except ValidationError as e:
            for key, value in e.message_dict.items():
                errors.append(f"{n} строка: {key}: {value[0]}")
        except ObjectDoesNotExist as e:
            errors.append(f"{n} строка: {e}")
        else:
            accruals.append(line)
    if errors:
        raise ParseFail(errors)
    if not accruals:
        raise ParseFail("Не найдено ни одной новой записи!")
    return accruals


def sale_report_parsing(file: ReadCsvBuffer) -> list[Accrual]:
    data = pd.read_csv(file).to_dict("records")
    if not all(key in data[0].keys() for key in sale_fields):
        raise ParseFail("Неизвестный вид отчета. Нет обязательных полей.")
    accruals = []
    errors = []
    for n, line in zip(range(1, len(data) + 1), data):
        try:
            # need to edit
            sum, name, base, person, date = [
                line[field] for field in sale_fields
            ]
            employee = async_to_sync(get_employee_by_name)(person)
            line = Accrual(
                employee=employee,
                sum=sum,
                name=name,
                date=datetime.strptime(date, date_format),
                base=base,
            )
            line.full_clean()
        except AlreadyExists:
            continue
        except ValidationError as e:
            for key, value in e.message_dict.items():
                errors.append(f"{n} строка: {key}: {value[0]}")
        except ObjectDoesNotExist as e:
            errors.append(f"{n} строка: {e}")
        else:
            accruals.append(line)
    if errors:
        raise ParseFail(errors)
    if not accruals:
        raise ParseFail("Не найдено ни одной новой записи!")
    return accruals
