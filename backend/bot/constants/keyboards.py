import enum

from bot.constants.exceptions import InnerFail
from bot.constants.states import States
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Buttons(enum.Enum):
    """Buttons."""

    TODAY = "Сегодня (Обновить)"
    REFRESH = "Обновить"


def keyboard_generator(list_of_lines: list[list[list | enum.Enum]]):
    result = []
    for line in list_of_lines:
        line_result = []
        for button in line:
            if isinstance(button, Buttons | States):
                line_result.append(
                    InlineKeyboardButton(
                        button.value, callback_data=button.name
                    )
                )
            elif isinstance(button, list):
                line_result.append(
                    InlineKeyboardButton(button[0], callback_data=button[1])
                )
            else:
                raise InnerFail(
                    f"{list_of_lines}\n"
                    f"Не могу сделать кнопу из: '{button}'. Проверь тип данных."
                )
        result.append(line_result)
    return InlineKeyboardMarkup(result)
