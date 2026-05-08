import asyncio
import datetime

BOT_VERSION = "2026-05-08-v34-refactored"

from config.logging import logger  # new structured logger

from config.settings import BOT_TOKEN, ADMIN_ID

logger.info(f"Bot starting | Version: {BOT_VERSION}")

# ... (rest of the file) ...

logger.info("Bot started successfully")