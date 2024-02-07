import enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def keyboard_generator(buttons):
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

    CHECK_IS_READY = "Чек готов"
    CONFIRMATION = "Подтвердить?"

    SCHEDULE = "Расписание"
    CREATE_REPORT = "Создать отчёт"


confirm_keyboard = keyboard_generator(
    [
        [Buttons.YES.value, Buttons.YES.name],
        [Buttons.NO.value, Buttons.NO.name],
    ]
)

start_keyboard = keyboard_generator(
    [[Buttons.RELOAD.value, Buttons.RELOAD.name]]
)

closing_confirmation_keyboard = keyboard_generator(
    [[Buttons.CONFIRMATION.value, Buttons.CONFIRMATION.name]]
)

close_check_keyboard = keyboard_generator(
    [[Buttons.CHECK_IS_READY.value, Buttons.CHECK_IS_READY.name]]
)

stuff_menu_keyboard = keyboard_generator(
    [
        [Buttons.SCHEDULE.value, Buttons.SCHEDULE.name],
        [Buttons.CREATE_REPORT.value, Buttons.CREATE_REPORT.name],
    ]
)
