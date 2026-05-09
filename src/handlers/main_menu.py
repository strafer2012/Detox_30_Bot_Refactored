from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite
from datetime import datetime, timedelta

from config.settings import DATABASE_PATH, ADMIN_ID

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
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT current_day, points, buddy_id, is_paid, timezone FROM users WHERE user_id = ?",
            (callback.from_user.id,)
        )
        row = await cursor.fetchone()
    
    if row:
        day, points, buddy_id, is_paid, tz = row
        tz = tz or 7
        
        # Локальное время пользователя
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(hours=tz)
        local_time_str = local_time.strftime("%H:%M")
        
        buddy_status = f"✅ Есть (@{buddy_id})" if buddy_id else "❌ Нет"
        paid_status = "✅ Оплачено" if is_paid else "❌ Бесплатный"
        
        text = f"📊 Ваш прогресс\n\n"
        f"🕒 Локальное время: {local_time_str} (UTC+{tz})\n"
        f"📅 День: {day or 1}/30\n"
        f"⭐ Баллов: {points or 0}\n"
        f"👥 Бадди: {buddy_status}\n"
        f"📆 Дней с бадди: 0\n"
        f"💎 Статус: {paid_status}"
    else:
        text = "Пользователь не найден. Нажмите /start."
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

print('✅ handlers/main_menu.py loaded with local time')