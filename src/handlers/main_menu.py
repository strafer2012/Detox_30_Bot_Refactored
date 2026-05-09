from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

from config.settings import DATABASE_PATH

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

@router.callback_query(F.data == "timezone")
async def timezone_menu(callback: CallbackQuery):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT timezone FROM users WHERE user_id = ?",
            (callback.from_user.id,)
        )
        row = await cursor.fetchone()
    
    tz = row[0] if row else 7
    
    text = f"🌍 Ваш текущий часовой пояс: UTC+{tz}"
    
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
    await callback.message.edit_text("🌍 Введите новый часовой пояс (UTC):
\nНапример: 3 (Москва), 7 (Красноярск), 10 (Владивосток)")
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
            await db.execute(
                "UPDATE users SET timezone = ? WHERE user_id = ?",
                (tz, message.from_user.id),
            )
            await db.commit()
        
        await message.answer(
            f"✅ Часовой пояс изменен на UTC+{tz}!")
        await state.clear()
    except ValueError:
        await message.answer("❌ Неверный часовой пояс. Введите число от -12 до 14.")

print('✅ handlers/main_menu.py loaded with timezone menu')