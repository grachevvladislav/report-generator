from redis.asyncio import Redis
from telegram.ext import ApplicationBuilder, PicklePersistence

from config import settings
from handlers.main_handlers import main_handler
from handlers.notifications import add_pay_notifications, notification_handler
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
        .read_timeout(30)
        .write_timeout(30)
        .persistence(persistence)
        .build()
    )
    if settings.check_mail:
        add_pay_notifications(app)
    app.add_handlers([main_handler, notification_handler])
    app.run_polling()


if __name__ == "__main__":
    main()
