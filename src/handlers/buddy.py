from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

import aiosqlite

from config.settings import DATABASE_PATH

router = Router()

# ====================== МЕНЮ БАДДИ ======================
@router.message(F.text == "Добавить / сменить бадди")
async def add_buddy_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Выбрать из закрытого чата", callback_data="buddy_closed_chat")],
            [InlineKeyboardButton(text="👤 Пригласить друга", callback_data="buddy_invite")]
        ]
    )
    await message.answer("👥 Выберите способ:", reply_markup=keyboard)

@router.callback_query(F.data == "buddy_closed_chat")
async def buddy_closed_chat(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 Напишите username без @ или переслайте профиль пользователя."
    )
    await callback.answer()

@router.callback_query(F.data == "buddy_invite")
async def buddy_invite(callback: CallbackQuery):
    await callback.message.edit_text(
        "👤 Пригласите друга по ссылке:\n\n"
        "https://t.me/your_bot?start=invite"
    )
    await callback.answer()

# ====================== МОИ ЗАПРОСЫ ======================
@router.message(F.text == "Мои запросы")
async def my_requests(message: Message):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM buddy_requests WHERE target_id = ? AND status = 'pending'",
            (message.from_user.id,)
        )
        requests = await cursor.fetchall()
    
    if not requests:
        await message.answer("Пока нет запросов от других. Когда кто-то выберет вас — уведомим!")
        return
    
    text = "📨 Ваши запросы:\n\n"
    for (user_id,) in requests:
        text += f"• ID: {user_id}\n"
    
    await message.answer(text)

# ====================== ИСТОРИЯ БАДДИ ======================
@router.message(F.text == "История бадди")
async def buddy_history(message: Message):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT buddy_id, created_at FROM buddy_pairs WHERE user1_id = ? OR user2_id = ? ORDER BY created_at DESC LIMIT 5",
            (message.from_user.id, message.from_user.id),
        )
        history = await cursor.fetchall()
    
    if not history:
        await message.answer("Пока нет истории бадди.")
        return
    
    text = "📅 История бадди:\n\n"
    for buddy_id, created_at in history:
        text += f"• {buddy_id} — {created_at}\n"
    
    await message.answer(text)

# ====================== СВЯЗЬ С БАДДИ ======================
@router.message(F.text == "Связь с бадди")
async def connect_with_buddy(message: Message):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT buddy_id FROM users WHERE user_id = ?",
            (message.from_user.id,)
        )
        row = await cursor.fetchone()
    
    if row and row[0]:
        await message.answer(f"👤 Ваш бадди: {row[0]}\n\nПишите ему лично!")
    else:
        await message.answer("У вас пока нет бадди. Выберите его в меню выше.")

# ====================== ОТМЕНИТЬ ЗАПРОС ======================
@router.message(F.text == "Отменить мой запрос")
async def cancel_request(message: Message):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM buddy_requests WHERE user_id = ? AND status = 'pending'",
            (message.from_user.id,)
        )
        await db.commit()
    
    await message.answer("✅ Ваш запрос отменён.")

# ====================== РАЗОРВАТЬ СВЯЗЬ ======================
@router.message(F.text == "Разорвать связь")
async def break_connection(message: Message):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET buddy_id = NULL WHERE user_id = ? OR buddy_id = ?",
            (message.from_user.id, message.from_user.id),
        )
        await db.commit()
    
    await message.answer("✅ Связь разорвана.")

print('✅ handlers/buddy.py loaded with full buddy system')