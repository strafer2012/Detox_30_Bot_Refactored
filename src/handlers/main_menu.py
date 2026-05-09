from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite
from datetime import datetime, timedelta
import time

from config.settings import DATABASE_PATH, ADMIN_ID

MENU_VERSION = "v55"

router = Router()

print(f'✅ handlers/main_menu.py loaded | Version: {MENU_VERSION}')

MAIN_MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="my_progress")],
        [InlineKeyboardButton(text="🏆 Мои бейджи", callback_data="my_badges")],
        [InlineKeyboardButton(text="🕐 Следующее сообщение", callback_data="next_message")],
        [InlineKeyboardButton(text="👥 Управление бадди", callback_data="buddy_management")],
        [InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="timezone")],
        [InlineKeyboardButton(text="💳 Оплатить марафон (999₽)", callback_data="pay_marathon")],
        [InlineKeyboardButton(text="📢 Пригласить друга", callback_data="invite_friend")],
        [InlineKeyboardButton(text="🔒 Зактытая группа", callback_data="closed_group")],
        [InlineKeyboardButton(text="🚨 Поддерзка", callback_data="support")],
        [InlineKeyboardButton(text=f"🔄 v{MENU_VERSION}", callback_data="noop")],
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
        
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(hours=tz)
        local_time_str = local_time.strftime("%H:%M")
        
        unique_id = int(time.time() * 1000) % 10000
        
        buddy_status = f"✅ Есть (@{buddy_id})" if buddy_id else "❌ Нет"
        paid_status = "✅ Оплачено" if is_paid else "❌ Бесплатный"
        
        text = f"📊 Ваш прогресс\n\n"
        f"🕒 Локальное время: {local_time_str} (UTC+{tz})\n"
        f"📅 День: {day or 1}/30\n"
        f"⭐ Баллов: {points or 0}\n"
        f"👥 Бадди: {buddy_status}\n"
        f"📆 Дней с бадди: 0\n"
        f"💎 Статус: {paid_status}\n"
        f"\n\n#{unique_id}"
    else:
        text = "Пользователь не найден. Нажмите /start."
    
    await callback.message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "my_badges")
async def my_badges(callback: CallbackQuery):
    text = "🏆 Ваши бейджи:\n\nУ вас пока нет бейджей. Продолжайте марафон!"
    await callback.message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "next_message")
async def next_message(callback: CallbackQuery):
    text = "🕐 Следующее сообщение:\n\nУтро: ~08:00\nОбразование: ~14:00\nВечер: ~20:30\n\nВаш часовой пояс: UTC+7"
    await callback.message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    text = "💳 Оплатить марафона (999₽):\n\nhttps://t.me/tribute/app?startapp=sUcf"
    await callback.message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    text = "📢 Пригласить друга: просто перешлите ему @Detox_30_bot"
    await callback.message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "closed_group")
async def closed_group(callback: CallbackQuery):
    text = "🔒 Зактытая группа: https://t.me/+6usILTSdMQIwMGU6"
    await callback.message.answer(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🚨 Отправьте сообщение, мы ответим в течение 12 часов ⬇️", reply_markup=MAIN_MENU_KEYBOARD)
    await state.set_state("waiting_support_message")
    await callback.answer()

@router.message(F.text)
async def process_support_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "waiting_support_message":
        return
    try:
        await message.bot.send_message(ADMIN_ID, f"🚨 Сообщение от {message.from_user.id}:\n\n{message.text}")
        await message.answer("✅ Сообщение отправлено!")
    except:
        await message.answer("❌ Ошибка.")
    await state.clear()

print('✅ handlers/main_menu.py loaded successfully')