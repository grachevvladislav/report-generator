import datetime

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from constants.keyboards import Buttons, start_keyboard, stuff_menu_keyboard
from constants.states import States
from google_sheet_backend import get_user_permissions
from handlers.report_generator import (
    counter_increase,
    make_report,
    wait_for_new_report,
)
from handlers.stuff import wait_for_file
from utils import PATTERN

from .schedule import show_schedule


async def start(update, context):
    context.bot_data.update(get_user_permissions())
    client_id = str(update.effective_chat["id"])
    if client_id in context.bot_data["admins_dict"].keys():
        return await show_schedule(update, context)
    elif client_id in context.bot_data["stuff_ids"]:
        await update.message.reply_text(
            "Управление ботом:",
            reply_markup=stuff_menu_keyboard,
        )
        return States.STUFF_MENU
    else:
        for stuff in context.bot_data["stuff_ids"]:
            if "request_send" not in context.bot_data.keys():
                await context.bot.send_message(
                    chat_id=stuff,
                    text=f"Поступил запрос от {update.effective_chat.first_name} "
                    f"{update.effective_chat.last_name}\n"
                    f"@{update.effective_chat.username}\n"
                    f"id:{update.effective_chat.id}",
                )
                context.bot_data["request_send"] = True
        if update.message:
            await update.message.reply_text(
                "Доступ пока закрыт, но запрос уже отправлен администратору!",
                reply_markup=start_keyboard,
            )
        else:
            query = update.callback_query
            await query.edit_message_text(
                "Доступ пока закрыт, но запрос уже отправлен администратору!\n"
                "Обновлено "
                + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                reply_markup=start_keyboard,
            )
        return States.PERMISSION_DENIED


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
                start, pattern=PATTERN.format(Buttons.RELOAD)
            ),
        ],
        States.STUFF_MENU: [
            CallbackQueryHandler(
                show_schedule, pattern=PATTERN.format(Buttons.SCHEDULE)
            ),
            CallbackQueryHandler(
                wait_for_file, pattern=PATTERN.format(Buttons.CREATE_REPORT)
            ),
        ],
        States.WAITING_FOR_FILE: [
            MessageHandler(filters.Document.ALL, make_report)
        ],
        States.CHECK_FILE: [
            CallbackQueryHandler(
                counter_increase, pattern=PATTERN.format(Buttons.YES)
            ),
            CallbackQueryHandler(
                wait_for_new_report, pattern=PATTERN.format(Buttons.NO)
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
