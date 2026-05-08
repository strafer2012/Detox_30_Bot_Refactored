from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite

from config.settings import ADMIN_ID, DATABASE_PATH

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active = (await cursor.fetchone())[0]
    
    text = f"📊 Краткая статистика

"
    f"👥 Активных пользователей: {active}
"
    f"📅 Версия: 2026-05-08-v34"
    
    await message.answer(text)


@router.message(Command("statsfull"))
async def cmd_statsfull(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, username, full_name, current_day, points, timezone, is_active
            FROM users 
            ORDER BY current_day DESC, points DESC 
            LIMIT 30
        """)
        rows = await cursor.fetchall()
    
    if not rows:
        await message.answer("Пользователи не найдены.")
        return
    
    text = "📊 Полная статистика (top 30)

"
    for row in rows:
        user_id, username, full_name, day, points, tz, active = row
        status = "✅" if active else "❌"
        text += f"{status} {user_id} | {full_name or username or 'N/A'} | День {day or 0} | {points or 0} баллов | UTC+{tz or 7}
"
    
    await message.answer(text)