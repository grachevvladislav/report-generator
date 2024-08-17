from bot.constants.keyboards import Buttons
from bot.constants.states import States
from bot.handlers.schedule import show_schedule
from bot.utils import PATTERN
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from .start import start

start_handler = CommandHandler("start", start)

main_handler = ConversationHandler(
    entry_points=[
        start_handler,
    ],
    persistent=True,
    name="main_handler",
    states={
        States.MAIN_MENU: [
            CallbackQueryHandler(
                start, pattern=PATTERN.format(Buttons.REFRESH.name)
            ),
            CallbackQueryHandler(
                show_schedule, pattern=PATTERN.format(States.SCHEDULE.name)
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
