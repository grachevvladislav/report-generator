from asgiref.sync import async_to_sync
from bot.handlers.main_handlers import main_handler
from bot.handlers.notifications import (
    add_pay_notifications,
    notification_handler,
)
from bot.persistence import RedisPersistence
from django.conf import settings
from django.core.management.base import BaseCommand
from redis.asyncio import Redis
from telegram.ext import ApplicationBuilder, PicklePersistence

from backend import settings


class Command(BaseCommand):
    """Start Telegram bot."""

    help = "Start Telegram bot."

    def handle(self, *args, **kwargs):
        """Bot launch point."""
        if settings.DEBUG:
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
            .token(settings.TELEGRAM_TOKEN)
            .read_timeout(30)
            .write_timeout(30)
            .persistence(persistence)
            .build()
        )
        if settings.CHECK_MAIL:
            async_to_sync(add_pay_notifications)(app)
        app.add_handlers([main_handler, notification_handler])
        app.run_polling()
