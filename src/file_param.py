import datetime
from calendar import monthrange
from decimal import Decimal

from borb.io.read.types import Decimal
from borb.pdf import (
    Alignment,
    FixedColumnWidthTable,
    FlexibleColumnWidthTable,
    Page,
    Paragraph,
    SingleColumnLayout,
    TableCell,
)

from constants.constants import custom_font
from constants.exceptions import InnerFail
from utils import surname_and_initials


def create_list(employee: dict) -> Page:
    page = Page()
    layout = SingleColumnLayout(page)
    layout.add(
        FixedColumnWidthTable(number_of_columns=1, number_of_rows=1)
        .add(
            TableCell(
                Paragraph(
                    f"Акт №{employee['document_counter']} от "
                    f"{datetime.datetime.today().strftime('%d.%m.%Y')}. "
                    f"За период с 1.{employee['report_interval'].strftime('%m.%Y')}г. по "
                    f"{monthrange(employee['report_interval'].year, employee['report_interval'].month)[1]}.{employee['report_interval'].strftime('%m.%Y')}г.",
                    font=custom_font,
                    font_size=Decimal(10),
                ),
                border_top=False,
                border_left=False,
                border_right=False,
            )
        )
        .set_padding_on_all_cells(
            Decimal(2), Decimal(2), Decimal(2), Decimal(2)
        )
    )
    if employee["tax"] == "СЗ":
        layout.add(
            Paragraph(
                f"Исполнитель: СЗ {employee['fio']}, ИНН: "
                f"{employee['inn']}, {employee['address']}, р/с "
                f"{employee['checking_account']}, {employee['bank']}, "
                f"{employee['bik']}, к/с {employee['correspondent_account']}\n"
                f"\nЗаказчик: {employee['customer_details']}\n\nОснование: "
                f"договор возмездного оказания услуг №"
                f"{employee['agreement_number']} от "
                f"{employee['agreement_date']}.",
                font=custom_font,
                font_size=Decimal(10),
                respect_newlines_in_text=True,
            )
        )
    elif employee["tax"] == "ИП":
        layout.add(
            Paragraph(
                f"Исполнитель: ИП {employee['fio']}, ОГРНИП: "
                f"{employee['ogrnip']}, ИНН: {employee['inn']}, "
                f"{employee['address']}, р/с {employee['checking_account']}, "
                f"{employee['bank']}, {employee['bik']}, к/с "
                f"{employee['correspondent_account']}\n\nЗаказчик: "
                f"{employee['customer_details']}\n\nОснование: договор "
                f"возмездного оказания услуг №{employee['agreement_number']} от"
                f" {employee['agreement_date']}.",
                font=custom_font,
                font_size=Decimal(10),
                respect_newlines_in_text=True,
            )
        )
    else:
        raise InnerFail(
            "Неизвестный режим налогооблажения: " + employee["tax"]
        )
    if employee["role"] == "Администратор":
        summ = str(
            (employee["admin_money"] * employee["percentage_of_sales"] / 100)
            + employee["admin_work_time"] * employee["admin_by_hours"]
        )
        table_data = [
            ["№ п/п", "Наименование услуги", "Кол-во", "Ед.", "Цена", "Сумма"],
            [
                "1",
                "Административная деятельность",
                str(employee["admin_work_time"]),
                "ч.",
                str(employee["admin_by_hours"]),
                str(employee["admin_work_time"] * employee["admin_by_hours"]),
            ],
            [
                "2",
                "Продажа абонементов",
                "1",
                "шт.",
                str(
                    employee["admin_money"]
                    * employee["percentage_of_sales"]
                    / 100
                ),
                str(
                    employee["admin_money"]
                    * employee["percentage_of_sales"]
                    / 100
                ),
            ],
            ["", "", "", "", "Итого:", summ],
            ["", "", "", "", "Без налога\n(НДС)", ""],
        ]
    elif employee["role"] == "Тренер":
        summ = 0
        lines = []
        counter = 0
        for key, count in employee["conducted_classes"].items():
            name, coast = key.split("$")
            counter += 1
            line_summ = float(coast) * float(count)
            summ += line_summ
            lines += [
                [str(counter), name, str(count), "шт.", coast, str(line_summ)]
            ]
        table_data = [
            ["№ п/п", "Наименование услуги", "Кол-во", "Ед.", "Цена", "Сумма"],
            *lines,
            ["", "", "", "", "Итого:", str(summ)],
            ["", "", "", "", "Без налога\n(НДС)", ""],
        ]
    else:
        raise InnerFail(
            "Неизвестная роль при  создании страницы: " + employee["role"]
        )
    table_separator = len(table_data) - 2
    main_table = FlexibleColumnWidthTable(
        number_of_columns=6, number_of_rows=len(table_data)
    )
    for line in table_data[:table_separator]:
        for field in line:
            main_table.add(
                TableCell(
                    Paragraph(
                        field,
                        font=custom_font,
                        font_size=Decimal(10),
                        text_alignment=Alignment.CENTERED,
                        horizontal_alignment=Alignment.CENTERED,
                        respect_newlines_in_text=True,
                        respect_spaces_in_text=True,
                    ),
                    border_width=Decimal(0.5),
                )
            )
    for line in table_data[table_separator:]:
        for field in line:
            main_table.add(
                TableCell(
                    Paragraph(
                        field,
                        font=custom_font,
                        font_size=Decimal(10),
                        text_alignment=Alignment.CENTERED,
                        horizontal_alignment=Alignment.CENTERED,
                        respect_newlines_in_text=True,
                        respect_spaces_in_text=True,
                    ),
                    border_left=False,
                    border_right=False,
                    border_bottom=False,
                    border_top=False,
                )
            )
    main_table.set_padding_on_all_cells(
        Decimal(10), Decimal(10), Decimal(10), Decimal(10)
    )
    layout.add(main_table)
    layout.add(
        Paragraph(
            f"Всего к оказано услуг на сумму {summ} руб.\n\nВышеперечисленные "
            f"услуги выполнены полностью и в срок. Заказчик претензий по "
            f"объему, качеству, срокам оказания услуг не имеет.",
            font=custom_font,
            font_size=Decimal(7),
            respect_newlines_in_text=True,
        )
    )

    signatures = [
        ["ЗАКАЗЧИК:", "ИСПОЛНИТЕЛЬ:"],
        [
            f'________________ / {employee["customer_short"]} /\n      Подпись',
            f'________________ / {surname_and_initials(employee["fio"])} /\n'
            f"        Подпись",
        ],
    ]
    signatures_table = FixedColumnWidthTable(
        number_of_columns=2, number_of_rows=2
    )
    for field in signatures[0]:
        signatures_table.add(
            TableCell(
                Paragraph(
                    field,
                    font=custom_font,
                    font_size=Decimal(10),
                    padding_left=Decimal(30),
                    respect_newlines_in_text=True,
                    respect_spaces_in_text=True,
                ),
                border_left=False,
                border_right=False,
                border_bottom=False,
                border_top=False,
            )
        )
    for field in signatures[1]:
        signatures_table.add(
            TableCell(
                Paragraph(
                    field,
                    font=custom_font,
                    font_size=Decimal(10),
                    padding_left=Decimal(20),
                    respect_newlines_in_text=True,
                    respect_spaces_in_text=True,
                ),
                border_left=False,
                border_right=False,
                border_bottom=False,
                border_top=False,
            )
        )
    signatures_table.no_borders()
    signatures_table.set_padding_on_all_cells(
        Decimal(2), Decimal(2), Decimal(2), Decimal(2)
    )
    layout.add(signatures_table)
    return page
