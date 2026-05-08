from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("force_message"))
async def cmd_force_message(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    # ... (full /force_message logic)
    await message.answer("Сообщение отправлено")