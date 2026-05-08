from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import aiosqlite
from datetime import datetime
import pytz

from config.settings import ADMIN_ID, DATABASE_PATH, MORNING_TIME, EDUCATION_TIME, EVENING_TIME

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("nextinfo"))
async def cmd_nextinfo(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используйте: /nextinfo <user_id>")
        return
    
    try:
        target_id = int(args[1])
    except ValueError:
        await message.answer("Неверный user_id.")
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT username, full_name, current_day, points, timezone, registration_date
            FROM users 
            WHERE user_id = ?
        """, (target_id,))
        row = await cursor.fetchone()
    
    if not row:
        await message.answer("Пользователь не найден.")
        return
    
    username, full_name, day, points, tz, reg_date = row
    tz = tz or 7
    day = day or 0
    points = points or 0
    
    # Локальное время пользователя
    now_utc = datetime.utcnow()
    local_tz = pytz.timezone(f"Etc/GMT{-tz}" if tz >= 0 else f"Etc/GMT+{abs(tz)}")
    local_time = now_utc.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    
    # Определяем следующее сообщение
    hour = local_time.hour
    if hour < 8:
        next_msg = "Утреннее правило (08:00)"
        next_time = local_time.replace(hour=8, minute=0, second=0)
    elif hour < 14:
        next_msg = "Образовательный блок (14:00)"
        next_time = local_time.replace(hour=14, minute=0, second=0)
    else:
        next_msg = "Вечерний отчёт (20:30)"
        next_time = local_time.replace(hour=20, minute=30, second=0)
    
    if next_time < local_time:
        next_time = next_time.replace(day=next_time.day + 1)
    
    delta = next_time - local_time
    hours_left = delta.seconds // 3600
    minutes_left = (delta.seconds % 3600) // 60
    
    text = f"🔍 Инфо пользователя {target_id}

"
    f"👤 {full_name or 'N/A'} (@{username or 'N/A'})
"
    f"📅 День: {day}
"
    f"🏆 Баллов: {points}
"
    f"🌍 Локальное время: {local_time.strftime('%H:%M')} (UTC+{tz})
"
    f"📅 Зарегистрирован: {reg_date or 'N/A'}

"
    f"🔔 Следующее сообщение: {next_msg}
"
    f"⏰ Осталось: {hours_left}ч {minutes_left}мин"
    
    await message.answer(text)