import asyncio
import datetime

BOT_VERSION = "2026-05-10-v40-fixed"

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import BOT_TOKEN, ADMIN_ID
from config.logging import logger as log

# Import all handlers
from handlers import start, daily, main_menu, buddy
from admin import router as admin_router

# Import monitoring
from monitoring.health_server import start_health_server
from monitoring.metrics import start_prometheus_server

bot = Bot(token=BOT_TOKEN)


async def main():
    log.info(f"Bot starting | Version: {BOT_VERSION}")
    
    # Start monitoring servers
    asyncio.create_task(start_health_server(port=8080))
    start_prometheus_server(port=9090)
    
    # Initialize database
    from database.database import init_db, migrate_database
    await init_db()
    await migrate_database()
    
    # Create dispatcher
    dp = Dispatcher(storage=MemoryStorage())
    
    # Include ALL routers
    dp.include_router(start.router)
    dp.include_router(daily.router)
    dp.include_router(main_menu.router)
    dp.include_router(buddy.router)
    dp.include_router(admin_router)
    
    # Delete webhook
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Webhook deleted")
    
    # Start scheduler
    try:
        import scheduler.scheduler as scheduler_module
        if hasattr(scheduler_module, 'start_scheduler'):
            asyncio.create_task(scheduler_module.start_scheduler())
            log.info("Scheduler started")
        else:
            log.warning("start_scheduler function not found")
    except Exception as e:
        log.warning(f"Scheduler error: {e}")
    
    log.info("Bot started successfully")
    
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())