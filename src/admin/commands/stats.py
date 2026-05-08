from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite

from config.settings import ADMIN_ID, DATABASE_PATH

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("nextinfo"))
async def cmd_nextinfo(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /nextinfo <user_id>")
        return
    
    try:
        target_id = int(args[1])
    except ValueError:
        await message.answer("Неверный user_id.")
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT username, full_name, current_day, points, timezone, registration_date
            FROM users 
            WHERE user_id = ?
        """, (target_id,))
        row = await cursor.fetchone()
    
    if not row:
        await message.answer("Пользователь не найден.")
        return
    
    username, full_name, day, points, tz, reg_date = row
    tz = tz or 7
    day = day or 0
    points = points or 0
    
    text = (
        f"🔍 Инфо пользователя {target_id}\n\n"
        f"👤 {full_name or 'N/A'} (@{username or 'N/A'})\n"
        f"📅 День: {day}\n"
        f"🏆 Баллов: {points}\n"
        f"🌍 Часовой пояс: UTC+{tz}\n"
        f"📅 Зарегистрирован: {reg_date or 'N/A'}"
    )
    
    await message.answer(text)