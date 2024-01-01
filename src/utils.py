from exceptions import ParseFail


def name_shortener(fio) -> str:
    full_name = fio.split(' ')
    if not len(full_name) == 3:
        raise ParseFail(f'Ошибка в ФИО:\n{fio}')
    return f'{full_name[0]} {full_name[1][0]}.'


def add_or_create(dictionary: dict, key: any, value: any) -> None:
    if key in dictionary.keys():
        dictionary[key] += value
    else:
        dictionary[key] = value
