from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = "🎯 Главное меню:"
    
    keyboard = InlineKeyboardMarkup(
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
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "buddy_management")
async def buddy_management(callback: CallbackQuery):
    text = "👥 Управление бадди:"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить / сменить бадди", callback_data="add_change_buddy")],
            [InlineKeyboardButton(text="📨 Мои запросы", callback_data="my_requests")],
            [InlineKeyboardButton(text="📅 История бадди", callback_data="buddy_history")],
            [InlineKeyboardButton(text="👤 Связь с бадди", callback_data="connect_buddy")],
            [InlineKeyboardButton(text="❌ Отменить мой запрос", callback_data="cancel_request")],
            [InlineKeyboardButton(text="❌ Разорвать связь", callback_data="break_connection")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

print('✅ handlers/start.py loaded with main menu + nested buddy menu')