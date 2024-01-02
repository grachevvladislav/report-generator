from decimal import Decimal

from borb.io.read.types import Decimal
from borb.pdf import Page, Paragraph, SingleColumnLayout, TableCell
from borb.pdf import FixedColumnWidthTable, FlexibleColumnWidthTable, Alignment

from utils import custom_font, surname_and_initials


def create_list(employee: dict) -> Page:
    print(employee)
    page = Page()
    layout = SingleColumnLayout(page)
    layout.add(
        FixedColumnWidthTable(number_of_columns=1, number_of_rows=1)
        .add(TableCell(Paragraph(
            f"Акт №{employee['document_counter']} от {employee['date']}. "
            f"За период с {employee['from']} по {employee['to']}.",
            font=custom_font, font_size=Decimal(10)
            ),
            border_top=False, border_left=False, border_right=False
        ))
        .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2),
                                  Decimal(2))
    )
    layout.add(Paragraph(
        f"Исполнитель: СЗ {employee['fio']}, {employee['inn']}, "
        f"{employee['address']}, р/с {employee['checking_account']}, "
        f"{employee['bank']}, {employee['bik']}, к/с "
        f"{employee['correspondent_account']}\n\nЗаказчик: "
        f"{employee['customer_details']}\n\nОснование: договор "
        f"возмездного оказания услуг №{employee['agreement_number']} от "
        f"{employee['agreement_date']}.",
        font=custom_font, font_size=Decimal(10), respect_newlines_in_text=True
    ))
    main_table = FlexibleColumnWidthTable(number_of_columns=6, number_of_rows=5)
    if employee['role'] == 'Администратор':
        summ = str(
            (employee['kpi_money'] * employee['percentage_of_sales'] / 100)
            + employee['admin_by_hours'] * employee['work_time']
        )
        table_data = [
            ["№ п/п", "Наименование услуги", "Кол-во", "Ед.", "Цена", "Сумма"],
            ['1', 'Административная деятельность', str(employee['work_time']),
             'ч.', str(employee['admin_by_hours']),
             str(employee['admin_by_hours'] * employee['work_time'])],
            ['2', 'Продажа абонементов', '1', 'шт.',
             str(employee['kpi_money'] * employee['percentage_of_sales'] / 100),
             str(employee['kpi_money'] * employee['percentage_of_sales'] / 100),
             ],
            ['', '', '', '', 'Итого:', summ],
            ['', '', '', '', 'Без налога\n(НДС)', '']
        ]
    else:
        return page

    for line in table_data[:3]:
        for field in line:
            main_table.add(TableCell(
                Paragraph(
                    field, font=custom_font, font_size=Decimal(10),
                    text_alignment=Alignment.CENTERED,
                    horizontal_alignment=Alignment.CENTERED,
                    respect_newlines_in_text=True, respect_spaces_in_text=True,
                ),
                border_width=Decimal(0.5)
            ))
    for line in table_data[3:]:
        for field in line:
            main_table.add(TableCell(
                Paragraph(
                    field, font=custom_font, font_size=Decimal(10),
                    text_alignment=Alignment.CENTERED,
                    horizontal_alignment=Alignment.CENTERED,
                    respect_newlines_in_text=True, respect_spaces_in_text=True
                ),
                border_left=False, border_right=False, border_bottom=False,
                border_top=False
            ))
    main_table.set_padding_on_all_cells(Decimal(10), Decimal(10), Decimal(10),
                                   Decimal(10))
    layout.add(main_table)
    layout.add(Paragraph(
        f"Всего к оказано услуг на сумму {summ} руб.\n\nВышеперечисленные "
        f"услуги выполнены полностью и в срок. Заказчик претензий по объему, "
        f"качеству, срокам оказания услуг не имеет.",
        font=custom_font, font_size=Decimal(7), respect_newlines_in_text=True
    ))

    signatures = [
        ['ЗАКАЗЧИК:', 'ИСПОЛНИТЕЛЬ:'],
        [f'________________ / {employee["customer_short"]} /\n      Подпись',
         f'________________ / {surname_and_initials(employee["fio"])} /\n'
         f'        Подпись'
         ]
    ]
    signatures_table = FixedColumnWidthTable(
        number_of_columns=2, number_of_rows=2)
    for field in signatures[0]:
        signatures_table.add(TableCell(
            Paragraph(
                field, font=custom_font, font_size=Decimal(10),
                padding_left=Decimal(30),
                respect_newlines_in_text=True, respect_spaces_in_text=True
            ),
            border_left=False, border_right=False, border_bottom=False,
            border_top=False
        ))
    for field in signatures[1]:
        signatures_table.add(TableCell(
            Paragraph(
                field, font=custom_font, font_size=Decimal(10),
                padding_left=Decimal(20),
                respect_newlines_in_text=True, respect_spaces_in_text=True
            ),
            border_left=False, border_right=False, border_bottom=False,
            border_top=False
        ))
    signatures_table.no_borders()
    signatures_table.set_padding_on_all_cells(
        Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    layout.add(signatures_table)
    return page
