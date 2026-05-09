from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

from config.settings import DATABASE_PATH

router = Router()

MAIN_MENU_TEXT = "🎯 Главное меню:"

MAIN_MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="my_progress")],
        [InlineKeyboardButton(text="🏆 Мои бейджи", callback_data="my_badges")],
        [InlineKeyboardButton(text="🕐 Следующее сообщение", callback_data="next_message")],
        [InlineKeyboardButton(text="👥 Управление бадди", callback_data="buddy_management")],
        [InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="timezone")],
        [InlineKeyboardButton(text="💳 Оплатить марафон (999₽)", callback_data="pay_marathon")],
        [InlineKeyboardButton(text="📢 Пригласить друга", callback_data="invite_friend")],
        [InlineKeyboardButton(text="🔒 Закрытая группа", callback_data="closed_group")],
        [InlineKeyboardButton(text="🚨 Поддержка", callback_data="support")],
    ]
)

@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT current_day, points, timezone FROM users WHERE user_id = ?",
            (callback.from_user.id,)
        )
        row = await cursor.fetchone()
    
    if row:
        day, points, tz = row
        text = f"📊 Ваш прогресс:\n\n"
        f"📅 День: {day or 0} / 30\n"
        f"🏆 Баллов: {points or 0}\n"
        f"🌍 Часовой пояс: UTC+{tz or 7}\n"
        f"🏅 Позиция в рейтинге: ТОП-50"
    else:
        text = "Пользователь не найден."
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "my_badges")
async def my_badges(callback: CallbackQuery):
    text = "🏆 Ваши бейджи:\n\n"
    f"🥇 Первый шаг\n"
    f"🥈 7 дней подряд\n"
    f"🥉 100 баллов\n"
    f"🎖️ 30 дней марафона"
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "next_message")
async def next_message(callback: CallbackQuery):
    text = "🕐 Следующее сообщение:\n\n"
    f"Образовательный блок (14:00)\n"
    f"Осталось: 2ч 17мин"
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "timezone")
async def timezone(callback: CallbackQuery):
    text = "🌍 Ваш часовой пояс: UTC+7\n\nНажмите /start и выберите 'Часовой пояс' для изменения."
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    text = "💳 Оплата марафона (999₽):\n\nНажмите кнопку ниже для оплаты."
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    text = "📢 Пригласить друга:\n\nhttps://t.me/your_bot?start=invite"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "closed_group")
async def closed_group(callback: CallbackQuery):
    text = "🔒 Закрытая группа:\n\nhttps://t.me/+your_closed_group_link"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    text = "🚨 Поддержка:\n\nНапишите @strafer2012 или нажмите кнопку 'Связь с поддержкой'.")
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

print('✅ handlers/main_menu.py loaded with edit mode')