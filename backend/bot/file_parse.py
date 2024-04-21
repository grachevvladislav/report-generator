import io

import pandas as pd
from constants.exceptions import ParseFail
from constants.roles import Roles
from google_sheet_backend import get_employees_info, set_default_classes
from models import Employees

role_fields = {
    "Администратор": ["Оплачено,\xa0₽", "Инициатор"],
    "Тренер": ["Сумма", "Автодействие", "Комментарий", "Сотрудник"],
}


def report_parsing(binary_file: bytearray, constants: dict) -> Employees:
    with io.BytesIO(binary_file) as memory_file:
        data = pd.read_csv(memory_file).to_dict("records")
    if all(
        key in data[0].keys() for key in role_fields[Roles.ADMINISTRATOR.value]
    ):
        mode = Roles.ADMINISTRATOR.value
    elif all(
        key in data[0].keys() for key in role_fields[Roles.TRAINER.value]
    ):
        mode = Roles.TRAINER.value
    else:
        raise ParseFail("Неизвестный вид отчета. Нет обязательных полей.")
    employees = get_employees_info(constants["employees"], mode)
    if mode == Roles.ADMINISTRATOR.value:
        # get_admins_working_time(employees, constants)
        fields = role_fields[mode]
        for line in data:
            employees.set_attribute(
                line[fields[1]], admin_money=float(line[fields[0]])
            )
    elif mode == Roles.TRAINER.value:
        set_default_classes(employees, constants)
        fields = role_fields[mode]
        for line in data:
            money, name, comment, person = [line[field] for field in fields]
            full_name = ""
            for field in [name, comment]:
                if field and not str(field) == "nan" and not field == "-":
                    full_name += str(field)
            employees.set_attribute(
                person,
                conducted_classes={full_name + "$" + str(money): 1},
            )
    return employees
