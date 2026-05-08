from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., min_length=10)
    ADMIN_ID: int = Field(..., gt=0)
    DATABASE_PATH: str = "detox30.db"
    CLOSED_CHAT_LINK: str = "https://t.me/+6usILTSdMQIwMGU6"

    # Message times (user local time)
    MORNING_TIME: str = "08:00"
    EDUCATION_TIME: str = "14:00"
    EVENING_TIME: str = "20:30"

    # Default timezone (UTC+7)
    USER_TIMEZONE: int = 7

    # Scheduler check interval (minutes)
    CHECK_INTERVAL: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()


# Convenience exports
BOT_TOKEN = settings.BOT_TOKEN
ADMIN_ID = settings.ADMIN_ID
DATABASE_PATH = settings.DATABASE_PATH
CLOSED_CHAT_LINK = settings.CLOSED_CHAT_LINK
MORNING_TIME = settings.MORNING_TIME
EDUCATION_TIME = settings.EDUCATION_TIME
EVENING_TIME = settings.EVENING_TIME
USER_TIMEZONE = settings.USER_TIMEZONE
CHECK_INTERVAL = settings.CHECK_INTERVAL

print("✅ settings.py loaded with Pydantic validation")