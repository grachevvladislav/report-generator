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
from bot.constants.exceptions import InnerFail
from bot.utils import surname_and_initials
from core.models import Employee

from backend.settings import CUSTOM_FONT

from .models import SalaryCertificate


def create_list(document: SalaryCertificate, owner: Employee) -> Page:
    page = Page()
    layout = SingleColumnLayout(page)
    layout.add(
        FixedColumnWidthTable(number_of_columns=1, number_of_rows=1)
        .add(
            TableCell(
                Paragraph(
                    f"Акт №{document.number} от "
                    f"{document.date_of_creation}. "
                    f"За период с {document.start_date.strftime('%d.%m.%Y')} по"
                    f" {document.end_date.strftime('%d.%m.%Y')}.",
                    font=CUSTOM_FONT,
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

    layout.add(
        Paragraph(
            f"Исполнитель: {document.contract.employee.tax_regime} "
            f"{document.contract.employee.full_name}, "
            f""
            f"{document.contract.employee.inn}, "
            f"{document.contract.employee.address}, р/с "
            f"{document.contract.employee.checking_account}, "
            f"{document.contract.employee.bank}, "
            f"{document.contract.employee.bik}, к/с "
            f"{document.contract.employee.correspondent_account}\n\n"
            f"Заказчик: ИП {owner.full_name}, ОГРНИП: {owner.ogrnip}, ИНН: "
            f"{owner.inn}, {owner.address}, р/с {owner.checking_account} в "
            f"банке {owner.bank}, БИК {owner.bik}"
            f"\n\nОснование: Договор "
            f"возмездного оказания услуг №{document.contract.number} от "
            f"{document.contract.start_date}.",
            font=CUSTOM_FONT,
            font_size=Decimal(10),
            respect_newlines_in_text=True,
        )
    )
    if document["role"] == "Администратор":
        summ = str(
            (document["admin_money"] * document["percentage_of_sales"] / 100)
            + document["admin_work_time"] * document["admin_by_hours"]
        )
        table_data = [
            ["№ п/п", "Наименование услуги", "Кол-во", "Ед.", "Цена", "Сумма"],
            [
                "1",
                "Административная деятельность",
                str(document["admin_work_time"]),
                "ч.",
                str(document["admin_by_hours"]),
                str(document["admin_work_time"] * document["admin_by_hours"]),
            ],
            [
                "2",
                "Продажа абонементов",
                "1",
                "шт.",
                str(
                    document["admin_money"]
                    * document["percentage_of_sales"]
                    / 100
                ),
                str(
                    document["admin_money"]
                    * document["percentage_of_sales"]
                    / 100
                ),
            ],
            ["", "", "", "", "Итого:", summ],
            ["", "", "", "", "Без налога\n(НДС)", ""],
        ]
    elif document["role"] == "Тренер":
        summ = 0
        lines = []
        counter = 0
        for key, count in document["conducted_classes"].items():
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
            "Неизвестная роль при  создании страницы: " + document["role"]
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
                        font=CUSTOM_FONT,
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
                        font=CUSTOM_FONT,
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
            font=CUSTOM_FONT,
            font_size=Decimal(7),
            respect_newlines_in_text=True,
        )
    )

    signatures = [
        ["ЗАКАЗЧИК:", "ИСПОЛНИТЕЛЬ:"],
        [
            f'________________ / {document["customer_short"]} /\n      Подпись',
            f'________________ / {surname_and_initials(document["fio"])} /\n'
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
                    font=CUSTOM_FONT,
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
                    font=CUSTOM_FONT,
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
