import asyncio
import datetime
import os

BOT_VERSION = "2026-05-10-v43-webhook-support"

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger

try:
    from src.config.settings import BOT_TOKEN, ADMIN_ID, WEBHOOK_URL, TELEGRAM_WEBHOOK_SECRET
    from src.config.logging import logger as log
except ImportError:
    from config.settings import BOT_TOKEN, ADMIN_ID, WEBHOOK_URL, TELEGRAM_WEBHOOK_SECRET
    from config.logging import logger as log

# Import all handlers
try:
    from src.handlers import start, daily, main_menu, buddy
    from src.handlers.admin import router as admin_router
except ImportError:
    from handlers import start, daily, main_menu, buddy
    from handlers.admin import router as admin_router

# Import monitoring
try:
    from src.monitoring.health_server import start_health_server
    from src.monitoring.metrics import start_prometheus_server
except ImportError:
    from monitoring.health_server import start_health_server
    from monitoring.metrics import start_prometheus_server

bot = Bot(token=BOT_TOKEN)


async def main():
    log.info(f"Bot starting | Version: {BOT_VERSION}")
    
    # Start monitoring servers
    asyncio.create_task(start_health_server(port=8080))
    start_prometheus_server(port=9090)
    
    # Initialize database
    try:
        from src.database.database import init_db, migrate_database
    except ImportError:
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
    
    if WEBHOOK_URL:
        # Webhook mode (recommended for Railway)
        log.info(f"Starting in WEBHOOK mode: {WEBHOOK_URL}")
        
        # Delete old webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Setup webhook
        app = web.Application()
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=TELEGRAM_WEBHOOK_SECRET or "detox30_super_secret_2026"
        )
        webhook_handler.register(app, path="/webhook/telegram")
        
        setup_application(app, dp, bot=bot)
        
        # Start health check
        async def health_handler(request):
            return web.json_response({"status": "healthy", "version": BOT_VERSION})
        app.router.add_get("/health", health_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        
        # Set webhook
        await bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=TELEGRAM_WEBHOOK_SECRET or "detox30_super_secret_2026",
            drop_pending_updates=True
        )
        log.info("Webhook set successfully")
        
        # Start scheduler
        try:
            from src.scheduler.scheduler import start_scheduler
            asyncio.create_task(start_scheduler())
            log.info("Scheduler started")
        except Exception as e:
            log.warning(f"Scheduler error: {e}")
        
        log.info("Bot started successfully in webhook mode")
        
        # Keep running
        await asyncio.Event().wait()
    else:
        # Polling mode (for local/dev)
        log.info("Starting in POLLING mode")
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("Webhook deleted")
        
        # Start scheduler
        try:
            from src.scheduler.scheduler import start_scheduler
            asyncio.create_task(start_scheduler())
            log.info("Scheduler started")
        except Exception as e:
            log.warning(f"Scheduler error: {e}")
        
        log.info("Bot started successfully")
        
        # Start polling
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())