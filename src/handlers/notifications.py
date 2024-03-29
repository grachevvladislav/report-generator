from telegram.ext import CallbackQueryHandler, ConversationHandler

from config import settings
from constants.keyboards import (
    Buttons,
    close_check_keyboard,
    closing_confirmation_keyboard,
)
from constants.states import States
from email_receive import get_payments
from google_sheet_backend import get_cashier_id


async def send_payment(context):
    """Send every payment as message."""
    for data in get_payments():
        text = "Новая онлайн оплата!\n\n"
        for key, value in data.items():
            text += key + ": " + value + "\n"
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=text,
            disable_notification=True,
            reply_markup=close_check_keyboard,
        )
    return States.WAITING_FOR_PAYMENT.name


def add_pay_notifications(app):
    """Add a job to the queue."""
    job_queue = app.job_queue
    chat_id = get_cashier_id()
    jobs = job_queue.get_jobs_by_name(chat_id)
    if jobs:
        for job in jobs:
            job.schedule_removal()
    job_queue.run_repeating(
        callback=send_payment,
        interval=int(settings.interval.get_secret_value()),
        chat_id=chat_id,
        first=1,
    )


async def close_check(update, context):
    """Delete a message after payment confirmation."""
    message = update.callback_query.message
    await context.bot.deleteMessage(
        message_id=message.message_id,
        chat_id=message.chat_id,
    )


async def closing_confirmation(update, context):
    query = update.callback_query
    await query.edit_message_text(
        query.message.text,
        reply_markup=closing_confirmation_keyboard,
    )
    return States.CONFIRMATION.name


closing_confirmation_handler = CallbackQueryHandler(
    callback=closing_confirmation,
    pattern="^" + Buttons.CHECK_IS_READY.name + "$",
)

notification_handler = ConversationHandler(
    entry_points=[
        closing_confirmation_handler,
    ],
    fallbacks=[],
    persistent=True,
    name="notification_handler",
    per_message=True,
    states={
        States.WAITING_FOR_PAYMENT.name: [
            CallbackQueryHandler(
                callback=closing_confirmation,
                pattern="^" + Buttons.CHECK_IS_READY.name + "$",
            )
        ],
        States.CONFIRMATION.name: [
            CallbackQueryHandler(
                callback=close_check,
                pattern="^" + Buttons.CONFIRMATION.name + "$",
            )
        ],
    },
)
