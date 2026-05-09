from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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
        [InlineKeyboardButton(text="🚨 Поддержка", callback_data="support")],
    ]
)

@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    text = "💳 Оплатить марафон (999₽):\n\nhttps://t.me/tribute/app?startapp=sUcf"
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
    
    # Отправить сообщение админу
    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"🚨 Сообщение от пользователя {message.from_user.id} (@{message.from_user.username or 'N/A'}):\n\n{message.text}"
        )
        await message.answer("✅ Сообщение отправлено! Мы ответим в течение 12 часов.")
    except:
        await message.answer("❌ Ошибка при отправке сообщения.")
    
    await state.clear()

print('✅ handlers/main_menu.py loaded with exact texts')