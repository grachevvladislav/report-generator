from pathlib import Path

from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont

from constants.exceptions import ParseFail


def surname_and_initials(fio: str) -> str:
    full_name = fio.split(" ")
    if not len(full_name) == 3:
        raise ParseFail(f"Ошибка в ФИО:\n{fio}")
    return f"{full_name[0]} {full_name[1][0]}.{full_name[2][0]}."


font_path = Path("files/Source Serif Pro.ttf")
custom_font = TrueTypeFont.true_type_font_from_file(font_path)


def make_short_name(name: str) -> str:
    fio_items = name.split(" ")
    if len(fio_items) < 2:
        fio_items.append("")
    return f"{fio_items[0]} {fio_items[1][0]}."
