PATTERN = "^{0}$"


async def send_or_edit_message(update, *args, **kwargs) -> None:
    query = update.callback_query
    if update.message:
        await update.message.reply_text(*args, **kwargs)
    else:
        await query.edit_message_text(*args, **kwargs)
