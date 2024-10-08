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
from constants import date_pattern
from core.models import Employee
from utils import format_money

from backend.settings import CUSTOM_FONT

from .models import SalaryCertificate


def create_list(document: SalaryCertificate, owner: Employee) -> Page:
    page = Page()
    layout = SingleColumnLayout(page)
    document_data = []
    for counter, field in enumerate(document.get_data()):
        document_data.append(
            map(
                str,
                [
                    counter + 1,
                    field.name,
                    # need to fix
                    "{0:.2f}".format(field.count).rstrip("0").rstrip("."),
                    field.unit,
                    format_money(field.price),
                    format_money(field.summ()),
                ],
            )
        )
    layout.add(
        FixedColumnWidthTable(number_of_columns=1, number_of_rows=1)
        .add(
            TableCell(
                Paragraph(
                    f"Акт №{document.number} от "
                    f"{document.date_of_creation.strftime(date_pattern)}г. "
                    f"За период с {document.start_date.strftime(date_pattern)} "
                    f"по {document.end_date.strftime(date_pattern)}.",
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
            f"Исполнитель: {document.contract.employee.for_doc()}\n\n"
            f"Заказчик: {owner.for_doc()}\n\n"
            f"Основание: Договор "
            f"возмездного оказания услуг №{document.contract.number} от "
            f"{document.contract.start_date.strftime(date_pattern)}г.",
            font=CUSTOM_FONT,
            font_size=Decimal(10),
            respect_newlines_in_text=True,
        )
    )
    table_data = [
        ["№ п/п", "Наименование услуги", "Кол-во", "Ед.", "Цена", "Сумма"],
        *document_data,
        ["", "", "", "", "Итого:", document.get_sum()],
        ["", "", "", "", "Без налога\n(НДС)", ""],
    ]
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
            f"Всего к оказано услуг на сумму {document.get_sum()}"
            f" руб.\n\nВышеперечисленные услуги выполнены полностью и в срок. "
            f"Заказчик претензий по объему, качеству, срокам оказания услуг не"
            f" имеет.",
            font=CUSTOM_FONT,
            font_size=Decimal(7),
            respect_newlines_in_text=True,
        )
    )

    signatures = [
        ["ЗАКАЗЧИК:", "ИСПОЛНИТЕЛЬ:"],
        [
            f"________________ / {document.contract.employee.short_name} /"
            f"\n      Подпись",
            f"________________ / {owner.short_name} /\n" f"        Подпись",
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
