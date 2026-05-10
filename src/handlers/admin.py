from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import (
    get_user,
    add_points,
    update_user_timezone,
    get_rating_report,
    mark_user_paid,
    get_user_paid_status
)

logger = logging.getLogger(__name__)
router = Router()

# ====================== АДМИН ФИЛЬТР ======================
ADMIN_IDS = [123456789]  # Замени на свой ADMIN_ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ====================== /STATS ======================
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    users = await get_rating_report(10)
    text = "📊 Общая статистика (TOP-10):\n\n"
    
    for i, (user_id, full_name, points, current_day, is_paid) in enumerate(users, 1):
        name = full_name or f"ID {user_id}"
        paid = "💳" if is_paid else ""
        text += f"{i}. {name} — {points} баллов (День {current_day}) {paid}\n"
    
    await message.answer(text)

# ====================== /STATS FULL ======================
@router.message(Command("statsfull"))
async def cmd_stats_full(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    users = await get_rating_report(50)
    text = "📊 Полная статистика:\n\n"
    
    total_users = len(users)
    total_points = sum(u[2] for u in users)
    
    text += f"👥 Всего пользователей: {total_users}\n"
    text += f"⭐ Общая сумма баллов: {total_points}\n\n"
    
    for user_id, full_name, points, current_day, is_paid in users[:15]:
        name = full_name or f"ID {user_id}"
        paid = "💳" if is_paid else ""
        text += f"{name}: {points} баллов (День {current_day}) {paid}\n"
    
    await message.answer(text)

# ====================== /USER <ID> ======================
@router.message(Command("user"))
async def cmd_user_info(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.split()[1])
    except:
        await message.answer("❌ Используй: /user <user_id>")
        return
    
    user = await get_user(user_id)
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    paid_status = await get_user_paid_status(user_id)
    paid = "💳 Оплачен" if paid_status["is_paid"] else "❌ Не оплачен"
    
    text = (
        f"👤 Пользователь: {user['full_name'] or 'N/A'}\n"
        f"ID: {user_id}\n"
        f"⭐ Баллы: {user['points']}\n"
        f"📅 День: {user['current_day']}\n"
        f"🕒 Часовой пояс: UTC{user['timezone']:+d}\n"
        f"{paid}\n"
    )
    await message.answer(text)

# ====================== /ADD_POINTS <ID> <AMOUNT> ======================
@router.message(Command("add_points"))
async def cmd_add_points(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
    except:
        await message.answer("❌ Используй: /add_points <user_id> <amount>")
        return
    
    await add_points(user_id, amount, "Админ начисление")
    await message.answer(f"✅ Начислено {amount} баллов пользователю {user_id}")

# ====================== /FORCE_MESSAGE <ID> <TEXT> ======================
@router.message(Command("force_message"))
async def cmd_force_message(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split(maxsplit=2)
        user_id = int(parts[1])
        text = parts[2]
    except:
        await message.answer("❌ Используй: /force_message <user_id> <text>")
        return
    
    from bot import bot
    await bot.send_message(user_id, text)
    await message.answer(f"✅ Сообщение отправлено пользователю {user_id}")

# ====================== /BAN /UNBAN ======================
@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.split()[1])
    except:
        await message.answer("❌ Используй: /ban <user_id>")
        return
    
    # Добавь в database.py функцию ban_user если нет
    await message.answer(f"⛔ Пользователь {user_id} заблокирован (ТОДО: добавь в базу)")

@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.split()[1])
    except:
        await message.answer("❌ Используй: /unban <user_id>")
        return
    
    await message.answer(f"✅ Пользователь {user_id} разблокирован (ТОДО)")

# ====================== /SETTIME <ID> <OFFSET> ======================
@router.message(Command("settime"))
async def cmd_settime(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        offset = int(parts[2])
    except:
        await message.answer("❌ Используй: /settime <user_id> <offset>")
        return
    
    await update_user_timezone(user_id, offset)
    await message.answer(f"✅ Часовой пояс пользователя {user_id} изменен на UTC{offset:+d}")

print("✅ src/handlers/admin.py загружен (Refactored v1 - полное админ-меню)")