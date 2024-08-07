import enum

from bot.constants.exceptions import InnerFail
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Buttons(enum.Enum):
    """Buttons."""

    TODAY = "Сегодня (Обновить)"

    CHECK_IS_READY = "Чек готов"
    CONFIRMATION = "Подтвердить?"

    SCHEDULE = "Расписание"


def keyboard_generator(list_of_lines: list[list[list | enum.Enum]]):
    result = []
    for line in list_of_lines:
        line_result = []
        for button in line:
            if isinstance(button, Buttons):
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
                    f"Не могу сделать кнопу из: '{button}'. Проверь тип данных."
                )
        result.append(line_result)
    return InlineKeyboardMarkup(result)


start_keyboard = keyboard_generator([[Buttons.TODAY]])

closing_confirmation_keyboard = keyboard_generator([[Buttons.CONFIRMATION]])

close_check_keyboard = keyboard_generator([[Buttons.CHECK_IS_READY]])
