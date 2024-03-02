from bot.constants.keyboards import Buttons, keyboard_generator
from bot.constants.states import States


async def report_menu(update, context):
    query = update.callback_query
    buttons = [[Buttons.CREATE, Buttons.LOAD_DATA], [Buttons.MENU]]
    await query.edit_message_text(
        "Выберете действие",
        reply_markup=keyboard_generator(buttons),
    )

    return States.CREATE_REPORT
