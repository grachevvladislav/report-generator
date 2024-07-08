import io

from borb.pdf import PDF, Document
from core.models import Employee
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from salary.make_pdf import create_list
from utils import (
    first_day_of_the_previous_month,
    last_day_of_the_previous_month,
)

from constants import non_employees_list

from .models import (
    Contract,
    SalaryCertificate,
    get_new_salary_certificate_number,
)


def create_pdf(сertificates) -> io.BytesIO:
    doc = Document()
    owner = Employee.objects.filter(is_owner=True).first()
    for certificate in сertificates:
        page = create_list(certificate, owner)
        doc.add_page(page)

    memory_file = io.BytesIO()
    PDF.dumps(memory_file, doc)
    memory_file.seek(0)
    return memory_file


def get_employee_by_name(name: str):
    if name in non_employees_list:
        return None
    parts = name.split(" ")
    if len(parts) < 2:
        raise ObjectDoesNotExist(f"Некорректный формат: {name}")
    surname = name.split(" ")[0]
    name = name.split(" ")[1]
    if name[1] == ".":
        employee = Employee.objects.filter(
            surname=surname, name__startswith=name[0]
        ).first()
    else:
        employee = Employee.objects.filter(surname=surname, name=name).first()
    if employee:
        return employee
    raise ObjectDoesNotExist(f"Сотрудник {surname} {name} не добавлен!")


def create_documents_for_last_month():
    active_contracts = Contract.objects.filter(
        Q(end_date__gte=last_day_of_the_previous_month()) | Q(end_date=None),
        start_date__lte=last_day_of_the_previous_month(),
    )
    print(active_contracts)
    counter = get_new_salary_certificate_number()
    docs = []
    for contract in active_contracts:
        if contract.start_date > first_day_of_the_previous_month():
            start_date = contract.start_date
        else:
            start_date = first_day_of_the_previous_month()
        doc = SalaryCertificate(
            number=counter,
            contract=contract,
            start_date=start_date,
            end_date=last_day_of_the_previous_month(),
        )
        docs.append(doc)
        counter += 1
    return docs
