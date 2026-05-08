from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite

from config.settings import ADMIN_ID, DATABASE_PATH

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /unban <user_id>")
        return
    
    try:
        target_id = int(args[1])
    except ValueError:
        await message.answer("Неверный user_id.")
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET is_active = 1 WHERE user_id = ?", (target_id,))
        await db.commit()
    
    await message.answer(f"✅ Пользователь {target_id} разбанен")