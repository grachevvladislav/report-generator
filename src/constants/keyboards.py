import enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard_from_list(buttons):
    result = [[]]
    for button in buttons:
        result[0].append(
            InlineKeyboardButton(button[0], callback_data=button[1])
        )
    return InlineKeyboardMarkup(result)


class Buttons(str, enum.Enum):
    """Buttons."""

    YES = "Да"
    NO = "Нет"
    RELOAD = "Обновить"


confirm_keyboard = keyboard_from_list(
    [
        [Buttons.YES.value, Buttons.YES.name],
        [Buttons.NO.value, Buttons.NO.name],
    ]
)

start_keyboard = keyboard_from_list(
    [[Buttons.RELOAD.value, Buttons.RELOAD.name]]
)
