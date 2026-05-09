from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite
import logging

from config.settings import DATABASE_PATH, ADMIN_ID

logger = logging.getLogger(__name__)
router = Router()

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
        [InlineKeyboardButton(text="🚨 Поддерзка", callback_data="support")],
    ]
)

@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    logger.info(f"my_progress called for user {callback.from_user.id}")
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT current_day, points, buddy_id, is_paid FROM users WHERE user_id = ?",
            (callback.from_user.id,)
        )
        row = await cursor.fetchone()
    
    logger.info(f"my_progress DB result: {row}")
    
    if row:
        day, points, buddy_id, is_paid = row
        buddy_status = f"✅ Есть (@{buddy_id})" if buddy_id else "❌ Нет"
        paid_status = "✅ Оплачено" if is_paid else "❌ Бесплатный"
        
        text = f"📊 Ваш прогресс\n\n"
        f"📅 День: {day or 1}/30\n"
        f"⭐ Баллов: {points or 0}\n"
        f"👥 Бадди: {buddy_status}\n"
        f"📆 Дней с бадди: 0\n"
        f"💎 Статус: {paid_status}"
    else:
        text = "Пользователь не найден. Нажмите /start."
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

print('✅ handlers/main_menu.py loaded with logging')