import asyncio
from aiogram import Bot
from config.settings import ADMIN_ID, BOT_TOKEN
from loguru import logger

_bot = None

async def init_bot():
    global _bot
    from bot import bot
    _bot = bot

async def notify_admin(text: str, important: bool = False):
    """Send notification to admin."""
    global _bot
    if _bot is None:
        await init_bot()
    
    prefix = "🚨 ВАЖНО: " if important else "📢 "
    try:
        await _bot.send_message(ADMIN_ID, f"{prefix}{text}", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


# Convenience functions for common events
async def notify_new_user(user_id: int, full_name: str, username: str = None):
    await notify_admin(
        f"🎉 Новый пользователь!
"
        f"👤 {full_name} (@{username or 'N/A'})
"
        f"🔗 ID: {user_id}"
    )

async def notify_course_completed(user_id: int, full_name: str, wants_to_continue: bool = False):
    text = (
        f"🎉 Пользователь завершил 7-дневный курс!
"
        f"👤 {full_name} (ID: {user_id})
"
    )
    if wants_to_continue:
        text += "
🚀 Хочет продолжить на платной основе!"
    await notify_admin(text, important=True)

async def notify_missed_reports(user_id: int, full_name: str, missed_days: int):
    await notify_admin(
        f"⚠️ Пользователь пропускает отчёты!
"
        f"👤 {full_name} (ID: {user_id})
"
        f"🕐 Пропущено дней: {missed_days}
"
        f"⚠️ Риск исключения из чата",
        important=True
    )

async def notify_error(error_msg: str, context: str = ""):
    await notify_admin(
        f"❌ Ошибка в боте!
"
        f"📢 {context}
"
        f"📝 {error_msg}",
        important=True
    )

print("✅ admin notifications system loaded")