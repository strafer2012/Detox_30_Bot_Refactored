from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

MAIN_MENU_TEXT = "🎯 Главное меню:"

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

@router.message(F.text == "/start")
async def show_main_menu(message: Message):
    await message.answer(MAIN_MENU_TEXT, reply_markup=MAIN_MENU_KEYBOARD)

@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    await callback.message.edit_text("📊 Ваш прогресс:\n\nДень: 5 / 30\nБаллов: 127\nПозиция в рейтинге: 23")
    await callback.answer()

@router.callback_query(F.data == "my_badges")
async def my_badges(callback: CallbackQuery):
    await callback.message.edit_text("🏆 Ваши бейджи:\n\n🥇 Первый шаг\n🥈 7 дней подряд\n🥉 100 баллов")
    await callback.answer()

@router.callback_query(F.data == "next_message")
async def next_message(callback: CallbackQuery):
    await callback.message.edit_text("🕐 Следующее сообщение:\n\nОбразовательный блок (14:00)\n\nОсталось: 2ч 17мин")
    await callback.answer()

@router.callback_query(F.data == "buddy_management")
async def buddy_management(callback: CallbackQuery):
    await callback.message.edit_text("👥 Управление бадди:\n\nВыберите действие из меню ниже.")
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

print('✅ handlers/main_menu.py loaded')