import asyncio
import datetime

BOT_VERSION = "2026-05-08-v35-refactored"

from config.logging import logger
from config.settings import BOT_TOKEN, ADMIN_ID

from monitoring.health_server import start_health_server

async def main():
    logger.info(f"Bot starting | Version: {BOT_VERSION}")
    
    # Start health check server in background
    asyncio.create_task(start_health_server(port=8080))
    
    # ... existing bot code ...
    
    logger.info("Bot started successfully")

if __name__ == "__main__":
    asyncio.run(main())