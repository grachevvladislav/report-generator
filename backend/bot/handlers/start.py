import datetime

from bot.constants.keyboards import Buttons, keyboard_generator
from bot.constants.states import States
from bot.crud import get_permission
from bot.utils import send_or_edit_message


async def start(update, context):
    permissions = await get_permission(update)
    if not permissions:
        await send_or_edit_message(
            update,
            "Доступ пока закрыт, но запрос уже отправлен администратору!\n"
            "Обновлено "
            + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            reply_markup=keyboard_generator([[Buttons.REFRESH]]),
        )
    else:
        message = "Доступные разделы:"
        buttons = [[]]
        for name, permission in permissions.items():
            if permission[0]:
                buttons[0].append(name)
        buttons.append([Buttons.REFRESH])
        await send_or_edit_message(
            update, message, reply_markup=keyboard_generator(buttons)
        )
    return States.MAIN_MENU
