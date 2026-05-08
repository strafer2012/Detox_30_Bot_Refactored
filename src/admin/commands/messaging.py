from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite

from config.settings import ADMIN_ID, DATABASE_PATH, BOT_TOKEN
from aiogram import Bot

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("force_message"))
async def cmd_force_message(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Используйте: /force_message <user_id> <текст>")
        return
    
    try:
        target_id = int(args[1])
        text = args[2]
    except ValueError:
        await message.answer("user_id должен быть числом.")
        return
    
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(target_id, text, parse_mode="HTML")
        await message.answer(f"✅ Сообщение отправлено пользователю {target_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")