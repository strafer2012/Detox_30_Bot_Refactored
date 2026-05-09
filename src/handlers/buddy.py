from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite
from datetime import datetime, timedelta

from config.settings import DATABASE_PATH

router = Router()

# ====================== ДОБАВИТЬ / СМЕНИТЬ БАДДИ ======================
@router.callback_query(F.data == "add_change_buddy")
async def add_change_buddy(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Выбрать из закрытого чата", callback_data="buddy_closed_chat")],
            [InlineKeyboardButton(text="👤 Пригласить друга", callback_data="buddy_invite")]
        ]
    )
    await callback.message.edit_text("👥 Выберите способ:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "buddy_closed_chat")
async def buddy_closed_chat(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💬 Напишите username без @ или переслайте профиль пользователя."
    )
    await state.set_state("waiting_buddy_username")
    await callback.answer()

@router.message(F.text)
async def process_buddy_request(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != "waiting_buddy_username":
        return
    
    username = message.text.strip().lstrip("@")
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Проверка лимита запросов в день
        today = datetime.now().date()
        cursor = await db.execute(
            "SELECT COUNT(*) FROM buddy_requests WHERE user_id = ? AND DATE(created_at) = ?",
            (message.from_user.id, today),
        )
        count = (await cursor.fetchone())[0]
        
        if count >= 5:
            await message.answer("❌ Вы достигли лимит 5 запросов в день.")
            await state.clear()
            return
        
        # Найти user_id по username
        cursor = await db.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (username,)
        )
        target = await cursor.fetchone()
        
        if not target:
            await message.answer("❌ Пользователь с таким username не найден.")
            await state.clear()
            return
        
        target_id = target[0]
        
        if target_id == message.from_user.id:
            await message.answer("❌ Нельзя отправить запрос себе.")
            await state.clear()
            return
        
        # Проверка, есть ли уже активная пара
        cursor = await db.execute(
            "SELECT buddy_id FROM users WHERE user_id = ?",
            (message.from_user.id,)
        )
        current_buddy = (await cursor.fetchone())[0]
        
        if current_buddy:
            await message.answer("❌ У вас уже есть бадди. Разорвите связь прежде.")
            await state.clear()
            return
        
        # Создать запрос
        await db.execute(
            "INSERT INTO buddy_requests (user_id, target_id, status, created_at) VALUES (?, ?, 'pending', ?)",
            (message.from_user.id, target_id, datetime.now()),
        )
        await db.commit()
    
    await message.answer("✅ Запрос отправлен! Пользователь получит уведомление.")
    await state.clear()

# ====================== МОИ ЗАПРОСЫ ======================
@router.callback_query(F.data == "my_requests")
async def my_requests(callback: CallbackQuery):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id FROM buddy_requests WHERE target_id = ? AND status = 'pending'",
            (callback.from_user.id,)
        )
        requests = await cursor.fetchall()
    
    if not requests:
        await callback.message.edit_text("📨 Пока нет запросов.")
        await callback.answer()
        return
    
    text = "📨 Ваши запросы:\n\n"
    keyboard_buttons = []
    
    for (user_id,) in requests:
        text += f"• ID: {user_id}\n"
        keyboard_buttons.append([
            InlineKeyboardButton(text=f"✅ Принять {user_id}", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton(text=f"❌ Отклонить {user_id}", callback_data=f"reject_{user_id}")
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# ====================== ИСТОРИЯ БАДДИ ======================
@router.callback_query(F.data == "buddy_history")
async def buddy_history(callback: CallbackQuery):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT buddy_id, created_at FROM buddy_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
            (callback.from_user.id,)
        )
        history = await cursor.fetchall()
    
    if not history:
        await callback.message.edit_text("📅 История бадди пуста.")
        await callback.answer()
        return
    
    text = "📅 История бадди:\n\n"
    for buddy_id, created_at in history:
        text += f"• {buddy_id} — {created_at}\n"
    
    await callback.message.edit_text(text)
    await callback.answer()

# ====================== РАЗОРВАТЬ СВЯЗЬ ======================
@router.callback_query(F.data == "break_connection")
async def break_connection(callback: CallbackQuery):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET buddy_id = NULL WHERE user_id = ? OR buddy_id = ?",
            (callback.from_user.id, callback.from_user.id),
        )
        await db.commit()
    
    await callback.message.edit_text("✅ Связь разорвана.")
    await callback.answer()

print('✅ handlers/buddy.py loaded with full system')