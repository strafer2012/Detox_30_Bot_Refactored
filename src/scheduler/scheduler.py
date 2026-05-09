import asyncio
import logging
import os
import signal
from datetime import datetime
import aiosqlite
import pytz

from config.settings import DATABASE_PATH
# RULES and EDUCATION_BLOCKS are placeholders (to be added to config in future)
RULES = {}
EDUCATION_BLOCKS = {}

from database import (
    get_rating_report, 
    save_message, 
    get_user, 
    add_points, 
    has_active_buddy,
    get_active_buddy
)

logger = logging.getLogger(__name__)

_bot = None
_shutdown_event = asyncio.Event()


async def init_bot():
    global _bot
    from bot import bot
    _bot = bot


async def safe_send_message(user_id: int, text: str, reply_markup=None, parse_mode=None):
    global _bot
    if _bot is None:
        await init_bot()
    try:
        return await _bot.send_message(user_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Send error to {user_id}: {e}")
        return None


# ====================== ЗАЩИТА ОТ ДУБЛИКАТОВ ======================
async def has_sent_today(user_id: int, message_type: str) -> bool:
    """Проверяет, было ли уже отправлено сообщение этого типа сегодня (по sent_at)"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("""
                SELECT 1 FROM sent_messages 
                WHERE user_id = ? AND message_type = ? 
                AND sent_at > datetime('now', '-1 day')
                LIMIT 1
            """, (user_id, message_type))
            return await cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Ошибка проверки дублирования {user_id}: {e}")
        return False


# ====================== КЛАВИАТУРЫ ======================
def get_morning_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принято", callback_data="morning_done")]
    ])


def get_education_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принято", callback_data="education_done")]
    ])


def get_evening_keyboard(day: int, has_buddy: bool):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    if has_buddy:
        text = "✅ Отчёт от бадди принял"
        callback = f"report_accept_{day}"
    else:
        text = "👥 Выберите себе бадди"
        callback = "menu_buddy"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=callback)]])


# ====================== ОТПРАВКА СООБЩЕНИЙ ======================
async def send_morning_message(user_id: int, day: int):
    if await has_sent_today(user_id, "morning"):
        return
    rule = RULES.get(day, "Правило дня")
    text = (
        f"🌅 Доброе утро! День {day}\n\n"
        f"{rule}\n\n"
        f"Прочитайте правило и нажмите кнопку ниже."
    )
    await safe_send_message(user_id, text, reply_markup=get_morning_keyboard())
    await save_message(user_id, text, "morning")
    logger.info(f"[Morning] День {day} → {user_id}")


async def send_education_message(user_id: int, day: int):
    if await has_sent_today(user_id, "education"):
        return
    material = EDUCATION_BLOCKS.get(day, "Материал дня")
    text = (
        f"📚 Образовательный блок — День {day}\n\n"
        f"{material}\n\n"
        f"Изучите материал и нажмите кнопку ниже."
    )
    await safe_send_message(user_id, text, reply_markup=get_education_keyboard())
    await save_message(user_id, text, "education")
    logger.info(f"[Education] День {day} → {user_id}")


async def send_evening_message(user_id: int, day: int):
    if await has_sent_today(user_id, "evening"):
        return
    # Правильный текст напоминания (по запросу пользователя)
    text = (
        f"Здравствуйте! 🌙\n\n"
        f"Напоминаю: до 21:00 нужно отправить отчёт своему бадди за День {day}.\n\n"
        f"Что нужно сделать:\n"
        f"1. Сделайте скриншот «Экранного времени»\n"
        f"2. Отправьте его своему бадди\n"
        f"3. Напишите ему коротко, что заметили сегодня\n\n"
        f"Проверьте скриншот своего бадди и напишите ему обратную связь.\n\n"
        f"Бадди уже ждет ваш отчёт! 💪\n\n"
        f"Если у вас ещё нет бадди — обязательно выберите его! 🤝\n"
        f"Это сильно повышает ответственность и эффективность марафона.\n\n"
        f"За каждую проверку отчета бадди вы получаете +5 баллов ежедневно 🎉"
    )
    has_buddy = await has_active_buddy(user_id)
    await safe_send_message(user_id, text, reply_markup=get_evening_keyboard(day, has_buddy))
    await save_message(user_id, text, "evening")
    logger.info(f"[Evening] День {day} → {user_id} (бадди: {has_buddy})")


async def send_daily_summary(user_id: int, day: int):
    if await has_sent_today(user_id, "summary"):
        return
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
            user_points = (await cursor.fetchone())[0] or 0

            cursor = await db.execute(
                "SELECT COUNT(*) + 1 FROM users WHERE points > ? AND is_active = 1",
                (user_points,)
            )
            rank = (await cursor.fetchone())[0]

            cursor = await db.execute(
                "SELECT full_name, points FROM users WHERE is_active = 1 ORDER BY points DESC LIMIT 10"
            )
            top_users = await cursor.fetchall()

        top_text = "🏆 ТОП-10 пользователей:\n" + "\n".join(
            f"{i}. {name} — {pts} баллов" for i, (name, pts) in enumerate(top_users, 1)
        )

        motivation = (
            f"\n💪 Завтра тебя ждёт День {day + 1}!\nВ 8:00 продолжаем марафон. Не пропусти!"
            if day < 30 else "\n🎉 Поздравляем с завершением 30-дневного марафона! Ты молодец!"
        )

        text = (
            f"🌙 ИТОГИ ДНЯ {day}\n\n"
            f"⭐ Твои баллы: {user_points}\n"
            f"🏅 Твоя позиция в рейтинге: {rank}\n\n"
            f"{top_text}\n"
            f"{motivation}"
        )

        await safe_send_message(user_id, text)
        await save_message(user_id, text, "summary")
        logger.info(f"[Summary] День {day} → {user_id} (позиция {rank})")

    except Exception as e:
        logger.error(f"[Summary] Ошибка у {user_id}: {e}")


# ====================== ОСНОВНАЯ ЛОГИКА ======================
async def send_daily_messages_by_local_time():
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute(
                "SELECT user_id, timezone, current_day FROM users WHERE is_active = 1"
            )
            users = await cursor.fetchall()

        now_utc = datetime.utcnow()

        for user_id, tz, current_day in users:
            tz = tz or 7
            try:
                if tz >= 0:
                    local_tz = pytz.timezone(f"Etc/GMT-{tz}")
                else:
                    local_tz = pytz.timezone(f"Etc/GMT+{abs(tz)}")
            except:
                local_tz = pytz.timezone("Etc/GMT-7")

            local_time = now_utc.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            local_hour_minute = local_time.strftime("%H:%M")

            if local_hour_minute == "08:00":
                await send_morning_message(user_id, current_day)
            elif local_hour_minute == "14:00":
                await send_education_message(user_id, current_day)
            elif local_hour_minute == "20:30":
                await send_evening_message(user_id, current_day)
            elif local_hour_minute == "21:00":
                await send_daily_summary(user_id, current_day)

    except Exception as e:
        logger.error(f"Ошибка в send_daily_messages_by_local_time: {e}")


# ====================== GRACEFUL SHUTDOWN + ЗАДЕРЖКА ======================
async def startup_delay():
    if os.getenv("RAILWAY_ENVIRONMENT") == "production":
        logger.info("⏳ Railway production detected. Waiting 180 seconds before starting...")
        await asyncio.sleep(180)
        logger.info("✅ Delay finished. Starting bot...")


def setup_signal_handlers():
    loop = asyncio.get_event_loop()

    def shutdown_handler():
        logger.info("🛑 Получен сигнал завершения. Останавливаем шедулер...")
        _shutdown_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown_handler)


async def start_universal_scheduler():
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    setup_signal_handlers()
    await startup_delay()

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        send_daily_messages_by_local_time,
        'cron',
        minute='*',
        max_instances=1,
        replace_existing=True,
        id="daily_messages_job"
    )
    scheduler.start()
    logger.info("✅ Universal Local Time Scheduler v7.6 (Refactored) запущен с защитой от дубликатов")

    await _shutdown_event.wait()
    logger.info("Завершение работы шедулера...")


if __name__ == "__main__":
    asyncio.run(start_universal_scheduler())
