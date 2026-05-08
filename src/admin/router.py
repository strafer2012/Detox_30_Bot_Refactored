from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import ADMIN_ID

from .commands import user_management, stats, messaging

router = Router()

# Подключаем модули
router.include_router(user_management.router)
router.include_router(stats.router)
router.include_router(messaging.router)


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("adminhelp"))
async def cmd_adminhelp(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав.")
        return
    
    help_text = '''🔧 КОМАНДЫ АДМИНА (Refactored v2)

/adminhelp — это сообщение
/version — версия бота

Пользователи:
/user <id> — инфо о пользователе
/setday <id> <day> — установить день
/settz <id> <tz> — установить часовой пояс

Статистика:
/stats — краткая статистика
/statsfull — полная статистика
/active — активные пользователи

Сообщения:
/force_message <id> <text> — принудительно отправить
/replay <id> <text> — ответить пользователю

Напишите /adminhelp для обновления списка.'''
    await message.answer(help_text)