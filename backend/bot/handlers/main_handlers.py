import datetime

from bot.constants.keyboards import Buttons, start_keyboard
from bot.constants.states import States
from bot.handlers.schedule import show_schedule
from bot.utils import PATTERN, send_or_edit_message
from core.models import BotRequest, Employee
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)


async def start(update, context):
    try:
        employee = await Employee.objects.aget(
            telegram_id=update.effective_chat["id"], is_active=True
        )
    except Employee.DoesNotExist:
        try:
            await BotRequest.objects.aget(telegram_id=update.effective_chat.id)
        except BotRequest.DoesNotExist:
            await BotRequest.objects.acreate(
                telegram_id=update.effective_chat.id,
                first_name=update.effective_chat.first_name,
                last_name=update.effective_chat.last_name,
                username=update.effective_chat.username,
            )
        await send_or_edit_message(
            update,
            "Доступ пока закрыт, но запрос уже отправлен администратору!\n"
            "Обновлено "
            + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            reply_markup=start_keyboard,
        )
        return States.PERMISSION_DENIED
    else:
        if employee.is_stuff or employee.сontract.template.hourly_payment:
            return await show_schedule(update, context)


start_handler = CommandHandler("start", start)

main_handler = ConversationHandler(
    entry_points=[
        start_handler,
    ],
    persistent=True,
    name="main_handler",
    states={
        States.PERMISSION_DENIED: [
            CallbackQueryHandler(
                start, pattern=PATTERN.format(Buttons.TODAY.name)
            ),
        ],
        States.SCHEDULE: [
            CallbackQueryHandler(
                show_schedule, pattern=PATTERN.format(r"[0-9]{2}\.[0-9]{4}")
            ),
        ],
    },
    fallbacks=[start_handler],
)
