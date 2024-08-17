from asgiref.sync import sync_to_async
from bot.constants.keyboards import keyboard_generator
from bot.constants.states import States
from bot.email_receive import get_payments
from bot.utils import PATTERN
from core.models import Default
from telegram.ext import CallbackQueryHandler, ConversationHandler

from backend import settings


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
            reply_markup=keyboard_generator([[States.WAITING_FOR_PAYMENT]]),
        )
    return States.WAITING_FOR_PAYMENT.name


async def add_pay_notifications(app):
    """Add a job to the queue."""
    job_queue = app.job_queue
    telegram_id = await sync_to_async(Default.get_default)(
        "cashier_telegram_id"
    )
    jobs = job_queue.get_jobs_by_name(telegram_id)
    if jobs:
        for job in jobs:
            job.schedule_removal()
    job_queue.run_repeating(
        callback=send_payment,
        interval=int(settings.INTERVAL),
        chat_id=telegram_id,
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
        reply_markup=keyboard_generator([[States.CONFIRMATION]]),
    )
    return States.CONFIRMATION.name


closing_confirmation_handler = CallbackQueryHandler(
    callback=closing_confirmation,
    pattern=PATTERN.format(States.WAITING_FOR_PAYMENT.name),
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
                pattern=PATTERN.format(States.WAITING_FOR_PAYMENT.name),
            )
        ],
        States.CONFIRMATION.name: [
            CallbackQueryHandler(
                callback=close_check,
                pattern=PATTERN.format(States.CONFIRMATION.name),
            )
        ],
    },
)
