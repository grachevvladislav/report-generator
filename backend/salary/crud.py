import io

from asgiref.sync import sync_to_async
from borb.pdf import PDF, Document
from core.models import Employee
from django.core.exceptions import ObjectDoesNotExist
from salary.make_pdf import create_list

from .constants import non_employees_list


def create_pdf(employees: list[Employee]) -> io.BytesIO:
    doc = Document()
    for employee in employees.get_active_employee():
        page = create_list(employee)
        doc.add_page(page)

    memory_file = io.BytesIO()
    PDF.dumps(memory_file, doc)
    memory_file.seek(0)
    return memory_file


async def get_employee_by_name(name: str):
    if name in non_employees_list:
        return None
    parts = name.split(" ")
    if len(parts) < 2:
        raise ObjectDoesNotExist(f"Некорректный формат: {name}")
    surname = name.split(" ")[0]
    name = name.split(" ")[1]
    if name[1] == ".":
        employee = await sync_to_async(
            Employee.objects.filter(
                surname=surname, name__startswith=name[0]
            ).first
        )()
    else:
        employee = await sync_to_async(
            Employee.objects.filter(surname=surname, name=name).first
        )()
    if employee:
        return employee
    raise ObjectDoesNotExist(f"Сотрудник {surname} {name} не добавлен!")
