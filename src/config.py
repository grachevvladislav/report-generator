from dotenv import find_dotenv
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    """Settings app."""

    telegram_token: SecretStr

    bot_settings_url: SecretStr
    schedule_url: SecretStr

    class Config:
        """Env settings."""

        env_file = find_dotenv(".env")
        env_file_encoding = "utf-8"


settings = Settings()
