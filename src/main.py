from redis.asyncio import Redis
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from config import settings
from constants.keyboards import Buttons
from constants.states import States
from handlers import (
    counter_increase,
    make_report,
    start_handler,
    wait_for_new_report,
)
from persistence import RedisPersistence


def main():
    """Application launch point."""
    if settings.debug:
        persistence = PicklePersistence(filepath="local_persistence")
    else:
        redis_instance = Redis(
            host=settings.redis_host.get_secret_value(),
            port=settings.redis_port.get_secret_value(),
            decode_responses=True,
        )
        persistence = RedisPersistence(redis_instance)
    app = (
        ApplicationBuilder()
        .token(settings.telegram_token.get_secret_value())
        .persistence(persistence)
        .build()
    )
    main_handler = ConversationHandler(
        entry_points=[start_handler],
        persistent=True,
        name="main_handler",
        states={
            States.PERMISSION_DENIED: [],
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
        },
        fallbacks=[start_handler],
    )
    app.add_handler(main_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
