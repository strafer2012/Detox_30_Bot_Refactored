import asyncio
import logging
from datetime import datetime
import aiosqlite
import pytz

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config.settings import ADMIN_ID, DATABASE_PATH

logger = logging.getLogger(__name__)

# Глобальная ссылка на bot
_bot = None

async def init_bot():
    global _bot
    from bot import bot
    _bot = bot

async def safe_send_message(user_id: int, text: str, reply_markup=None):
    global _bot
    if _bot is None:
        await init_bot()
    try:
        return await _bot.send_message(
            user_id, text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Failed to send message to {user_id}: {e}")
        return None


async def start_scheduler():
    """Start the scheduler for daily messages."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler(timezone="UTC")
    
    # Добавляем задачи
    scheduler.add_job(
        increment_day_at_midnight,
        'cron',
        minute='*',
        max_instances=1,
        replace_existing=True
    )
    
    scheduler.add_job(
        send_forced_report_21,
        'cron',
        hour=21,
        minute=0,
        max_instances=1,
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started successfully")
    
    # Консервируем scheduler для доступа извне
    global _scheduler
    _scheduler = scheduler


# Заглушки для функций из старого кода
async def increment_day_at_midnight():
    logger.info("Midnight job - day increment")
    # TODO: добавить логику смены дня

async def send_forced_report_21():
    logger.info("21:00 forced report job")
    # TODO: добавить логику принудительных отчётов

print('✅ scheduler.py loaded with start_scheduler')