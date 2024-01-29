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
