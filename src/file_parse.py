import io
from docxtpl import DocxTemplate
import pandas as pd
from utils import add_or_create
from exceptions import ParseFail


def report_parsing(
        employees: dict, binary_file: bytearray, constants: dict) -> None:
    with io.BytesIO(binary_file) as memory_file:
        data = pd.read_csv(memory_file).to_dict('records')
    for record in data:
        money = float(record['Оплачено,\xa0₽']) * constants['percentage_of_sales'] / 100
        try:
            add_or_create(
                dictionary=employees[record['Инициатор']],
                key='kpi_money',
                value=money
            )
        except KeyError:
            raise ParseFail(f'Неизвестный кассир:\n{record["Инициатор"]}')


def create_doc(context):
    for tmp in context.values():
        #context['date'] = datetime.today().strftime('%d.%m.%Y')
        print(tmp)
        print()
        doc = DocxTemplate('files/pattern.docx')
        doc.render(tmp)
        doc.save("new.docx")
        break