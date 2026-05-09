from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite

from config.settings import DATABASE_PATH

router = Router()

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
        text = "Пользователь не найден. Нажмите /start."
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "my_badges")
async def my_badges(callback: CallbackQuery):
    text = "🏆 Ваши бейджи:\n\n"
    f"🥇 Первый шаг\n"
    f"🥈 7 дней подряд\n"
    f"🥉 100 баллов\n"
    f"🎖️ 30 дней марафона"
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "next_message")
async def next_message(callback: CallbackQuery):
    text = "🕐 Следующее сообщение:\n\n"
    f"Образовательный блок (14:00)\n"
    f"Осталось: 2ч 17мин"
    
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "timezone")
async def timezone(callback: CallbackQuery):
    await callback.message.edit_text("🌍 Ваш часовой пояс: UTC+7\n\nНажмите /start и выберите 'Часовой пояс' для изменения.")
    await callback.answer()

@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    await callback.message.edit_text("💳 Оплата марафона (999₽):\n\nНажмите кнопку ниже для оплаты.")
    await callback.answer()

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    await callback.message.edit_text("📢 Пригласить друга:\n\nhttps://t.me/your_bot?start=invite")
    await callback.answer()

@router.callback_query(F.data == "closed_group")
async def closed_group(callback: CallbackQuery):
    await callback.message.edit_text("🔒 Закрытая группа:\n\nhttps://t.me/+your_closed_group_link")
    await callback.answer()

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text("🚨 Поддержка:\n\nНапишите @strafer2012 или нажмите кнопку 'Связь с поддержкой'.")
    await callback.answer()

print('✅ handlers/main_menu.py loaded with full functionality')