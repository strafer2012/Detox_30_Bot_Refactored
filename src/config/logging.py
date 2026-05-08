import os
import sys
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def setup_logging():
    logger.remove()
    
    # Console (development)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # File (JSON structured)
    logger.add(
        "logs/bot_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        serialize=True,
    )
    
    # Sentry (production monitoring)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_logging = LoggingIntegration(level="ERROR", event_level="ERROR")
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging],
            traces_sample_rate=0.1,  # 10% of transactions
            environment=os.getenv("ENVIRONMENT", "production"),
            release=os.getenv("RELEASE", "unknown"),
        )
        logger.info("Sentry monitoring enabled")
    
    logger.info("Logging configured (loguru + structured JSON + Sentry)")

setup_logging()