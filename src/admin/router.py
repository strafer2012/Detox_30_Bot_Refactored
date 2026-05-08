from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("adminhelp"))
async def cmd_adminhelp(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав.")
        return
    
    help_text = '''КОМАНДЫ АДМИНА (Refactored v2)

/adminhelp — это сообщение
/version — версия

УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ:
/setday, /settz, /settime, /ban, /unban, /reset, /user

СТАТИСТИКА:
/stats, /statsfull, /active, /inactive

ОТПРАВКА СООБЩЕНИЙ:
/force_message, /replay, /next

Напишите /adminhelp для полного списка.''' 
    await message.answer(help_text)