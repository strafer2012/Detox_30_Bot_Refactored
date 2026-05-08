import asyncio
import datetime

BOT_VERSION = "2026-05-08-v36-refactored"

from config.logging import logger
from config.settings import BOT_TOKEN, ADMIN_ID

from monitoring.health_server import start_health_server
from monitoring.metrics import start_prometheus_server, update_active_users

async def main():
    logger.info(f"Bot starting | Version: {BOT_VERSION}")
    
    # Start monitoring servers
    asyncio.create_task(start_health_server(port=8080))
    start_prometheus_server(port=9090)
    
    # ... existing bot code ...
    
    logger.info("Bot started successfully")