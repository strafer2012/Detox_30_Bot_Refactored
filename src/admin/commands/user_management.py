from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite

from config.settings import ADMIN_ID, DATABASE_PATH

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("user"))
async def cmd_user(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /user <user_id>")
        return
    
    try:
        target_id = int(args[1])
    except ValueError:
        await message.answer("user_id должен быть числом.")
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT username, full_name, current_day, points, timezone FROM users WHERE user_id = ?",
            (target_id,)
        )
        row = await cursor.fetchone()
    
    if row:
        username, full_name, day, points, tz = row
        text = f"👤 Пользователь {target_id}

"
        f"👤 {full_name or 'N/A'} (@{username or 'N/A'})
"
        f"📅 День: {day or 0}
"
        f"🏆 Баллов: {points or 0}
"
        f"🌍 Часовой пояс: UTC+{tz or 7}"
        await message.answer(text)
    else:
        await message.answer("Пользователь не найден.")