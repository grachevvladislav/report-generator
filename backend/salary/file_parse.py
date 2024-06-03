from datetime import datetime

import pandas as pd
from asgiref.sync import async_to_sync
from core.models import Employee
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from pandas._typing import ReadCsvBuffer

from .crud import get_employee_by_name
from .exceptions import AlreadyExists, ParseFail
from .models import Accrual

role_fields = {
    Employee.Role.ADMIN.value: ["Оплачено,\xa0₽", "Инициатор"],
    Employee.Role.TRAINER.value: [
        "Сумма",
        "Автодействие",
        "Комментарий",
        "Сотрудник",
        "Дата начисления",
    ],
}
date_format = "%d.%m.%Y %H:%M"


def report_parsing(file: ReadCsvBuffer) -> list[Accrual]:
    data = pd.read_csv(file).to_dict("records")
    if all(
        key in data[0].keys() for key in role_fields[Employee.Role.ADMIN.value]
    ):
        mode = Employee.Role.ADMIN.value
    elif all(
        key in data[0].keys()
        for key in role_fields[Employee.Role.TRAINER.value]
    ):
        mode = Employee.Role.TRAINER.value
    else:
        raise ParseFail("Неизвестный вид отчета. Нет обязательных полей.")
    accruals = []
    if mode == Employee.Role.ADMIN.value:
        pass
        # get_admins_working_time(employees, constants)
        # fields = role_fields[mode]
        # for line in data:
        #     employees.set_attribute(
        #         line[fields[1]], admin_money=float(line[fields[0]])
        #     )
    elif mode == Employee.Role.TRAINER.value:
        fields = role_fields[mode]
        errors = []
        for n, line in zip(range(1, len(data) + 1), data):
            try:
                sum, name, base, person, date = [
                    line[field] for field in fields
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
