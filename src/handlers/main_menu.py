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
    text = "📊 Ваш прогресс:\n\nДень: 1/30\nБаллов: 0\nБадди: Хет"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "my_badges")
async def my_badges(callback: CallbackQuery):
    text = "🏆 Ваши бейджи:\n\nУ вас пока нет бейджей. Продолжайте марафон!"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "next_message")
async def next_message(callback: CallbackQuery):
    text = "🕐 Следующее сообщение:\n\nУтро: ~08:00\nОбразование: ~14:00\nВечер: ~20:30\n\nВаш часовой пояс: UTC+7"
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

@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    text = "💳 Оплатить марафона (999₽):\n\nhttps://t.me/tribute/app?startapp=sUcf"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    text = "📢 Пригласить друга: просто перешлите ему @Detox_30_bot"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "closed_group")
async def closed_group(callback: CallbackQuery):
    text = "🔒 Закрытая группа: https://t.me/+6usILTSdMQIwMGU6"
    await callback.message.edit_text(text, reply_markup=MAIN_MENU_KEYBOARD)
    await callback.answer()

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🚨 Отправьте сообщение, мы ответим в течение 12 часов ⬇️")
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