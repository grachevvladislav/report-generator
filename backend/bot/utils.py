from telegram.error import BadRequest

from backend.settings import logger

PATTERN = "^{0}$"


async def send_or_edit_message(update, *args, **kwargs) -> None:
    query = update.callback_query
    if update.message:
        await update.message.reply_text(*args, **kwargs)
        logger.info(
            f'Sent message to {update.effective_chat["id"]}: '
            f"{str(args)} {str(kwargs)}"
        )
    else:
        try:
            logger.info(
                f'Changed message for {update.effective_chat["id"]}: '
                f"{str(args)} {str(kwargs)}"
            )
            await query.edit_message_text(*args, **kwargs)
        except BadRequest:
            logger.info(
                f'Changed message for {update.effective_chat["id"]}: BadRequest err'
            )
