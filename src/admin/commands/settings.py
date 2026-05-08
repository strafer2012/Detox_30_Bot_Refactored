from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite

from config.settings import ADMIN_ID, DATABASE_PATH

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("settime"))
async def cmd_settime(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 4:
        await message.answer("Используйте: /settime <user_id> <тип> <HH:MM>")
        return
    
    try:
        target_id = int(args[1])
        msg_type = args[2].lower()
        time_str = args[3]
    except ValueError:
        await message.answer("Неверные параметры.")
        return
    
    if msg_type not in ["morning", "education", "evening"]:
        await message.answer("Тип должен быть: morning, education или evening.")
        return
    
    # Для простоты пока просто уведомляем
    await message.answer(f"✅ Время {msg_type} для {target_id} изменено на {time_str} (TODO: сохранить в БД)")