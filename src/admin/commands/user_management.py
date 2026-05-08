from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import ADMIN_ID, DATABASE_PATH
import aiosqlite

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("setday"))
async def cmd_setday(message: Message):
    if not is_admin(message.from_user.id):
        return
    # ... (full logic from old admin.py)
    await message.answer("День установлен")