import locale

from dotenv import find_dotenv
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    """Settings app."""

    telegram_token: SecretStr

    bot_settings_url: SecretStr
    schedule_url: SecretStr

    redis_port: SecretStr
    redis_host: SecretStr

    imap_ssl_host: SecretStr
    imap_username: SecretStr
    imap_password: SecretStr
    imap_from_email: SecretStr
    interval: SecretStr

    debug: bool = False

    class Config:
        """Env settings."""

        env_file = find_dotenv(".env")
        env_file_encoding = "utf-8"


settings = Settings()

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
