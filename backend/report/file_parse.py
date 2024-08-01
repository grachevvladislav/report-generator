from datetime import datetime

import pandas as pd
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from exceptions import AlreadyExists, ParseFail
from report.models import Accrual, Sale
from salary.crud import get_employee_by_name

from .constants import date_format, sale_fields, trainer_fields


def trainer_report_parsing(file) -> list[Accrual]:
    try:
        data = pd.read_csv(filepath_or_buffer=file, sep=";").to_dict("records")
        if not all(key in data[0].keys() for key in trainer_fields):
            raise ParseFail("Неизвестный вид отчета. Нет обязательных полей.")
    except IndexError:
        raise ParseFail("Ошибка в файле.")
    accruals = []
    errors = []
    for n, line in zip(range(1, len(data) + 1), data):
        try:
            sum, name, base, person, date = [
                line[field] for field in trainer_fields
            ]
            employee = get_employee_by_name(person)
            line = Accrual(
                employee_id=lambda: employee.id if employee else None,
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


def sale_report_parsing(file) -> list[Accrual]:
    data = pd.read_csv(filepath_or_buffer=file, sep=";").to_dict("records")
    if not all(key in data[0].keys() for key in sale_fields):
        raise ParseFail("Неизвестный вид отчета. Нет обязательных полей.")
    accruals = []
    errors = []
    for n, line in zip(range(1, len(data) + 1), data):
        try:
            sum, person, name, date, client = [
                line[field] for field in sale_fields
            ]
            employee = get_employee_by_name(person)
            line = Sale(
                employee_id=lambda: employee.id if employee else None,
                sum=sum,
                name=name,
                client=client,
                date=datetime.strptime(date, date_format),
            )
            line.full_clean()
        except (AlreadyExists, ValidationError):
            continue
        except ObjectDoesNotExist as e:
            errors.append(f"{n} строка: {e}")
        else:
            accruals.append(line)
    if errors:
        raise ParseFail(errors)
    if not accruals:
        raise ParseFail("Не найдено ни одной новой записи!")
    return accruals
