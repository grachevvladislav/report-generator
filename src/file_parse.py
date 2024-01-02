import datetime
import io
from calendar import monthrange

import pandas as pd
from borb.pdf import PDF, Document

from exceptions import ParseFail
from file_creator import create_list


def report_parsing(employees: dict, binary_file: bytearray) -> None:
    with io.BytesIO(binary_file) as memory_file:
        data = pd.read_csv(memory_file).to_dict("records")
    for record in data:
        money = float(record["Оплачено,\xa0₽"])
        try:
            employees[record["Инициатор"]]["kpi_money"] = money
        except KeyError:
            raise ParseFail(f'Неизвестный кассир:\n{record["Инициатор"]}')


def create_pdf(
    employees: dict[dict], last_month: datetime.datetime, constants: dict
) -> io.BytesIO:
    doc = Document()
    constants["date"] = datetime.datetime.today().strftime("%d.%m.%Y")
    constants["from"] = f"1.{last_month.month}.{last_month.year}г."
    constants["to"] = (
        f"{monthrange(last_month.year, last_month.month)[1]}."
        f"{last_month.month}.{last_month.year}г"
    )
    for employee in employees.values():
        constants["document_counter"] += 1
        employee.update(constants)
        page = create_list(employee)
        doc.add_page(page)

    memory_file = io.BytesIO()
    PDF.dumps(memory_file, doc)
    memory_file.seek(0)
    return memory_file
