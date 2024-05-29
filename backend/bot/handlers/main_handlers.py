import datetime

from bot.constants.keyboards import (
    Buttons,
    start_keyboard,
    stuff_menu_keyboard,
)
from bot.constants.states import States
from bot.handlers.schedule import show_schedule
from bot.handlers.stuff import report_menu
from bot.utils import PATTERN, send_or_edit_message
from core.models import BotRequest, Employee
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)
from utils import get_related_object


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
        if await get_related_object(employee, "role") == Employee.Role.ADMIN:
            return show_schedule(update, context)
        elif employee.role == Employee.Role.STUFF:
            await send_or_edit_message(
                update,
                "Управление ботом:",
                reply_markup=stuff_menu_keyboard,
            )
            return States.STUFF_MENU


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
        States.STUFF_MENU: [
            CallbackQueryHandler(
                show_schedule, pattern=PATTERN.format(Buttons.SCHEDULE.name)
            ),
            CallbackQueryHandler(
                report_menu,
                pattern=PATTERN.format(Buttons.CREATE_REPORT.name),
            ),
            CallbackQueryHandler(
                start, pattern=PATTERN.format(Buttons.MENU.name)
            ),
        ],
        States.SCHEDULE: [
            CallbackQueryHandler(
                show_schedule, pattern=PATTERN.format(r"[0-9]{2}\.[0-9]{4}")
            ),
            CallbackQueryHandler(
                start, pattern=PATTERN.format(Buttons.MENU.name)
            ),
        ],
    },
    fallbacks=[start_handler],
)
