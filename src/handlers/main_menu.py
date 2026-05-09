from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import logging

from database import get_user, get_active_buddy, get_buddy_username

logger = logging.getLogger(__name__)
router = Router()

# ====================== ГЛАВНОЕ МЕНЮ ======================
MAIN_MENU = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="my_progress")],
    [InlineKeyboardButton(text="👥 Бадди", callback_data="menu_buddy")],
    [InlineKeyboardButton(text="🏆 Рейтинг", callback_data="menu_rating")],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
    [InlineKeyboardButton(text="💳 Оплатить (999₽)", callback_data="pay_marathon")],
    [InlineKeyboardButton(text="📢 Пригласить друга", callback_data="invite_friend")],
])

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("🏠 Главное меню:", reply_markup=MAIN_MENU)
    await callback.answer()

@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала нажми /start")
        await callback.answer()
        return

    buddy_id = await get_active_buddy(callback.from_user.id)
    buddy_text = "✅ Есть" if buddy_id else "❌ Нет"

    text = (
        f"📊 Твой прогресс\n\n"
        f"📅 День: {user['current_day']}/30\n"
        f"⭐ Баллы: {user['points']}\n"
        f"👥 Бадди: {buddy_text}\n"
        f"🕒 Часовой пояс: UTC{user['timezone']:+d}"
    )

    await callback.message.edit_text(text, reply_markup=MAIN_MENU)
    await callback.answer()

@router.callback_query(F.data == "menu_rating")
async def menu_rating(callback: CallbackQuery):
    from database import get_rating_report
    top = await get_rating_report(10)
    
    text = "🏆 ТОП-10:\n\n"
    for i, (uid, name, pts, day, paid) in enumerate(top, 1):
        n = name or f"ID {uid}"
        text += f"{i}. {n} — {pts} баллов (День {day})\n"
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU)
    await callback.answer()

@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: CallbackQuery):
    text = "⚙️ Настройки\n\nВыбери действие в меню ниже."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕒 Изменить часовой пояс", callback_data="change_timezone")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    text = "💳 Оплатить марафон (999₽):\n\nhttps://t.me/tribute/app?startapp=sUcf"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU)
    await callback.answer()

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    text = "📢 Пригласить друга:\nПросто перешли ему @Detox_30_bot"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU)
    await callback.answer()

print("✅ src/handlers/main_menu.py загружен (Refactored v3 - чистая версия)")