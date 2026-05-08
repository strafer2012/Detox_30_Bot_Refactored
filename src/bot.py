import asyncio
import logging
import datetime

BOT_VERSION = "2026-05-08-v31-refactored"

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import BOT_TOKEN, ADMIN_ID
from database.database import init_db, migrate_database

# Импорты handlers
from handlers import start, daily

# ... (cleaned version of bot.py with better structure) ... 
print(f"=== BOT STARTED | Version: {BOT_VERSION} | {datetime.datetime.now()} ===")