from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite

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
            "SELECT current_day, points, buddy_id, is_paid FROM users WHERE user_id = ?",
            (callback.from_user.id,)
        )
        row = await cursor.fetchone()
    
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
        text = "Пользователь не найден."
    
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "timezone")
async def timezone_menu(callback: CallbackQuery):
    text = "🌍 Ваш текущий часовой пояс: UTC+7"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оставить", callback_data="keep_timezone")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="change_timezone")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "keep_timezone")
async def keep_timezone(callback: CallbackQuery):
    await callback.message.edit_text("✅ Часовой пояс оставлен.", reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "change_timezone")
async def change_timezone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🌍 Введите новый часовой пояс (UTC):\n\nНапример: 3, 7, 10")
    await state.set_state("waiting_new_timezone")
    await callback.answer()

@router.message(F.text.regexp(r"^-?\d{1,2}$"))
async def process_new_timezone(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "waiting_new_timezone":
        return
    try:
        tz = int(message.text)
        if not -12 <= tz <= 14:
            raise ValueError
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (tz, message.from_user.id))
            await db.commit()
        await message.answer(f"✅ Часовой пояс изменен на UTC+{tz}!")
        await state.clear()
    except ValueError:
        await message.answer("❌ Неверный часовой пояс.")

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🚨 Отправьте сообщение, мы ответим в течение 12 часов ⬇️", reply_markup=MAIN_MENU_KEYBOARD)
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

print('✅ handlers/main_menu.py loaded with all requirements')