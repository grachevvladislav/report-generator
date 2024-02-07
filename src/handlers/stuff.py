from constants.states import States


async def wait_for_file(update, context):
    query = update.callback_query
    await query.edit_message_text(
        "Отправьте отчет о продажах или проведенных занятиях"
    )
    return States.WAITING_FOR_FILE
