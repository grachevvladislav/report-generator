from bot.constants.exceptions import ParseFail

PATTERN = "^{0}$"


def surname_and_initials(fio: str) -> str:
    full_name = fio.split(" ")
    if not len(full_name) == 3:
        raise ParseFail(f"Ошибка в ФИО:\n{fio}")
    return f"{full_name[0]} {full_name[1][0]}.{full_name[2][0]}."


async def send_or_edit_message(update, *args, **kwargs) -> None:
    query = update.callback_query
    if update.message:
        await update.message.reply_text(*args, **kwargs)
    else:
        await query.edit_message_text(*args, **kwargs)
