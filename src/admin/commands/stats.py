from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import ADMIN_ID
from database.database import get_user_stats, get_all_active_users

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    active_users = await get_all_active_users()
    total = len(active_users)
    
    text = f"📊 Краткая статистика

"
    f"👥 Всего активных: {total}
"
    f"📅 День: сегодня
"
    f"🔄 Версия: 2026-05-08-v34"
    
    await message.answer(text)