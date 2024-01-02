from pathlib import Path

from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont

from exceptions import ParseFail


def name_shortener(fio: str) -> str:
    full_name = fio.split(' ')
    if not len(full_name) == 3:
        raise ParseFail(f'Ошибка в ФИО:\n{fio}')
    return f'{full_name[0]} {full_name[1][0]}.'


def surname_and_initials(fio: str) -> str:
    full_name = fio.split(' ')
    if not len(full_name) == 3:
        raise ParseFail(f'Ошибка в ФИО:\n{fio}')
    return f'{full_name[0]} {full_name[1][0]}.{full_name[2][0]}.'


def add_or_create(dictionary: dict, key: any, value: any) -> None:
    if key in dictionary.keys():
        dictionary[key] += value
    else:
        dictionary[key] = value


font_path = Path('files/Source Serif Pro.ttf')
custom_font = TrueTypeFont.true_type_font_from_file(font_path)
