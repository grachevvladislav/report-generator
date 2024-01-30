import enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Buttons(str, enum.Enum):
    """Buttons."""

    YES = "Да"
    NO = "Нет"


confirm_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                Buttons.YES.value, callback_data=Buttons.YES.name
            ),
            InlineKeyboardButton(
                Buttons.NO.value, callback_data=Buttons.NO.name
            ),
        ]
    ]
)


def keyboard_from_list(buttons):
    result = [[]]
    for button in buttons:
        result[0].append(
            InlineKeyboardButton(button[0], callback_data=button[1])
        )
    return InlineKeyboardMarkup(result)
