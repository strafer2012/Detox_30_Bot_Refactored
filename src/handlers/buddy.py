from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import (
    create_buddy_request,
    get_pending_requests_for_user,
    accept_buddy_request,
    decline_buddy_request,
    get_active_buddy,
    break_buddy_pair,
    get_buddy_history,
    get_buddy_username,
    get_daily_buddy_requests_count
)

logger = logging.getLogger(__name__)
router = Router()

class BuddyStates(StatesGroup):
    waiting_for_username = State()

# ====================== МЕНЮ БАДДИ ======================
@router.callback_query(F.data == "menu_buddy")
async def menu_buddy(callback: CallbackQuery):
    buddy_id = await get_active_buddy(callback.from_user.id)
    
    if buddy_id:
        buddy_name = await get_buddy_username(buddy_id)
        text = f"👥 Твой бадди: {buddy_name} (ID: {buddy_id})"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📩 Посмотреть запросы", callback_data="my_buddy_requests")],
            [InlineKeyboardButton(text="📅 История партнёрства", callback_data="buddy_history")],
            [InlineKeyboardButton(text="❌ Разорвать связь", callback_data="break_buddy")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
        ])
    else:
        text = "👥 У тебя пока нет бадди"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Найти / Пригласить бадди", callback_data="find_buddy")],
            [InlineKeyboardButton(text="📩 Мои запросы", callback_data="my_buddy_requests")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
        ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# ====================== ПОИСК БАДДИ ======================
@router.callback_query(F.data == "find_buddy")
async def find_buddy(callback: CallbackQuery, state: FSMContext):
    count = await get_daily_buddy_requests_count(callback.from_user.id)
    if count >= 5:
        await callback.message.edit_text("❌ Вы достигли лимит 5 запросов в день.")
        await callback.answer()
        return

    await callback.message.edit_text(
        "🔍 Напиши username без @ или переслай профиль пользователя."
    )
    await state.set_state(BuddyStates.waiting_for_username)
    await callback.answer()

@router.message(BuddyStates.waiting_for_username)
async def process_buddy_username(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    
    # Находим user_id по username
    from database import get_user_by_username  # добавь эту функцию в database.py если нет
    target = await get_user_by_username(username)
    
    if not target:
        await message.answer("❌ Пользователь не найден.")
        await state.clear()
        return
    
    target_id = target["user_id"]
    
    if target_id == message.from_user.id:
        await message.answer("❌ Нельзя отправить запрос себе.")
        await state.clear()
        return
    
    success = await create_buddy_request(message.from_user.id, target_id)
    
    if success:
        await message.answer("✅ Запрос на бадди отправлен!")
    else:
        await message.answer("❌ Запрос уже отправлен или пользователь занят.")
    
    await state.clear()

# ====================== МОИ ЗАПРОСЫ ======================
@router.callback_query(F.data == "my_buddy_requests")
async def my_buddy_requests(callback: CallbackQuery):
    requests = await get_pending_requests_for_user(callback.from_user.id)
    
    if not requests:
        await callback.message.edit_text("📨 Пока нет запросов на бадди.")
        await callback.answer()
        return
    
    text = "📨 Запросы на бадди:\n\n"
    keyboard = []
    
    for req_id, requester_id, username, full_name in requests:
        name = full_name or username or f"ID {requester_id}"
        text += f"• {name}\n"
        keyboard.append([
            InlineKeyboardButton(text=f"✅ Принять", callback_data=f"accept_buddy_{req_id}"),
            InlineKeyboardButton(text=f"❌ Отклонить", callback_data=f"decline_buddy_{req_id}")
        ])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_buddy")])
    
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@router.callback_query(F.data.startswith("accept_buddy_"))
async def accept_buddy(callback: CallbackQuery):
    req_id = int(callback.data.split("_")[2])
    result = await accept_buddy_request(req_id, callback.from_user.id)
    
    if result["success"]:
        await callback.message.edit_text("✅ Бадди успешно добавлен!")
    else:
        await callback.message.edit_text(f"❌ {result.get('error', 'Ошибка')}")
    await callback.answer()

@router.callback_query(F.data.startswith("decline_buddy_"))
async def decline_buddy(callback: CallbackQuery):
    req_id = int(callback.data.split("_")[2])
    await decline_buddy_request(req_id, callback.from_user.id)
    await callback.message.edit_text("❌ Запрос отклонён.")
    await callback.answer()

# ====================== РАЗОРВАТЬ СВЯЗЬ ======================
@router.callback_query(F.data == "break_buddy")
async def break_buddy_connection(callback: CallbackQuery):
    result = await break_buddy_pair(callback.from_user.id)
    
    if result["success"]:
        await callback.message.edit_text("✅ Связь разорвана.")
    else:
        await callback.message.edit_text("❌ У тебя нет активного бадди.")
    await callback.answer()

# ====================== ИСТОРИЯ ======================
@router.callback_query(F.data == "buddy_history")
async def show_buddy_history(callback: CallbackQuery):
    history = await get_buddy_history(callback.from_user.id, limit=5)
    
    if not history:
        await callback.message.edit_text("📅 История партнёрства пуста.")
        await callback.answer()
        return
    
    text = "📅 История бадди:\n\n"
    for buddy_id, started_at, ended_at in history:
        name = await get_buddy_username(buddy_id)
        text += f"• {name} — с {started_at[:10]}\n"
    
    await callback.message.edit_text(text)
    await callback.answer()

print("✅ src/handlers/buddy.py загружен (Refactored v2 - полная система)")