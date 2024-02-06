import datetime

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from constants.keyboards import Buttons, start_keyboard
from constants.states import States
from google_sheet_backend import get_cashier_id, get_user_permissions
from handlers.report_generator import (
    counter_increase,
    make_report,
    wait_for_new_report,
)

from .notifications import add_pay_notifications, close_check
from .schedule import show_schedule


async def start(update, context):
    context.user_data.update(get_user_permissions())
    client_id = str(update.effective_chat["id"])
    if client_id == get_cashier_id():
        return add_pay_notifications(update, context)
    elif client_id in context.user_data["admins_dict"].keys():
        return await show_schedule(update, context)
    elif client_id in context.user_data["stuff_ids"]:
        await update.message.reply_text(
            "Отправьте отчет о продажах или проведенных занятиях"
        )
        return States.WAITING_FOR_FILE
    else:
        for stuff in context.user_data["stuff_ids"]:
            if "request_send" not in context.user_data.keys():
                await context.bot.send_message(
                    chat_id=stuff,
                    text=f"Поступил запрос от {update.effective_chat.first_name} "
                    f"{update.effective_chat.last_name}\n"
                    f"@{update.effective_chat.username}\n"
                    f"id:{update.effective_chat.id}",
                )
                context.user_data["request_send"] = True
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
                start, pattern="^" + str(Buttons.RELOAD.name) + "$"
            ),
        ],
        States.WAITING_FOR_PAYMENT: [
            CallbackQueryHandler(
                close_check,
                pattern="^" + str(Buttons.CHECK_IS_READY.name) + "$",
            )
        ],
        States.WAITING_FOR_FILE: [
            MessageHandler(filters.Document.ALL, make_report)
        ],
        States.CHECK_FILE: [
            CallbackQueryHandler(
                counter_increase, pattern="^" + str(Buttons.YES.name) + "$"
            ),
            CallbackQueryHandler(
                wait_for_new_report,
                pattern="^" + str(Buttons.NO.name) + "$",
            ),
        ],
        States.ADMINS_MENU: [],
        States.SCHEDULE: [
            CallbackQueryHandler(
                show_schedule,
            ),
        ],
    },
    fallbacks=[start_handler],
)
