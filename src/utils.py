from constants.exceptions import ParseFail

PATTERN = "^{0}$"


def surname_and_initials(fio: str) -> str:
    full_name = fio.split(" ")
    if not len(full_name) == 3:
        raise ParseFail(f"Ошибка в ФИО:\n{fio}")
    return f"{full_name[0]} {full_name[1][0]}.{full_name[2][0]}."


def key_name_generator(name: str) -> str:
    fio_items = name.split(" ")
    if len(fio_items) < 2:
        fio_items.append(" ")
    return f"{fio_items[0]} {fio_items[1][0]}."
