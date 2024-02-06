from constants.keyboards import keyboard_generator
from constants.states import States
from google_sheet_backend import get_admin_schedule


async def show_schedule(update, context):
    query = update.callback_query
    if query:
        data_delta = query.data
    else:
        data_delta = None
    schedule, buttons = get_admin_schedule(
        context.user_data["admins_dict"][str(update.effective_chat["id"])],
        data_delta,
    )
    if update.message:
        await update.message.reply_text(
            "\n".join(schedule),
            reply_markup=keyboard_generator(buttons),
        )
    else:
        await query.edit_message_text(
            "\n".join(schedule),
            reply_markup=keyboard_generator(buttons),
        )
    return States.SCHEDULE
