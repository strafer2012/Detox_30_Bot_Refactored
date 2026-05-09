from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import aiosqlite

from config.settings import DATABASE_PATH

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    # Автоматически создаём пользователя, если его нет
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name, registration_date)
            VALUES (?, ?, ?, CURRENT_DATE)
        """, (message.from_user.id, message.from_user.username, message.from_user.full_name))
        await db.commit()
    
    text = "🚀 Добро пожаловать в Detox 30!\n\nПоздравляю! Вы зарегистрированы.\n\nВаш первый день марафона начнётся в ближайшие 08:00 по вашему времени.\n\nИспользуйте меню ниже: ⬇️"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="my_progress")],
            [InlineKeyboardButton(text="🏆 Мои бейджи", callback_data="my_badges")],
            [InlineKeyboardButton(text="🕐 Следующее сообщение", callback_data="next_message")],
            [InlineKeyboardButton(text="👥 Управление бадди", callback_data="buddy_management")],
            [InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="timezone")],
            [InlineKeyboardButton(text="💳 Оплатить марафон (999₽)", callback_data="pay_marathon")],
            [InlineKeyboardButton(text="📢 Пригласить друга", callback_data="invite_friend")],
            [InlineKeyboardButton(text="🔒 Закрытая группа", callback_data="closed_group")],
            [InlineKeyboardButton(text="🚨 Поддерзка", callback_data="support")],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard)

print('✅ handlers/start.py loaded with auto user creation')