import os
import sys
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def setup_logging():
    """Configure loguru with structured logging and optional Sentry integration."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler (pretty for development)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # File handler (JSON for production / structured logs)
    logger.add(
        "logs/bot_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        serialize=True,  # JSON structured logs
    )
    
    # Optional Sentry integration
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_logging = LoggingIntegration(
            level="ERROR",        # Capture error and above as breadcrumbs
            event_level="ERROR"   # Send errors as events
        )
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging],
            traces_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "production"),
        )
        logger.info("Sentry integration enabled")
    
    logger.info("Logging configured (loguru + structured JSON + Sentry-ready)")


# Auto-setup when imported
setup_logging()