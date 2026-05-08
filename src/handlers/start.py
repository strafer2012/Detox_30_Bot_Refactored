from aiogram import Router, F

from config.messages import (...)
from src.utils.rate_limiter import rate_limit, buddy_rate_limit

# ... (existing code) ...

@router.message(Command("start"))
@rate_limit(max_messages=3, window_seconds=60)
async def cmd_start(message: Message):
    # ... existing code ...

@router.message(F.text == "Найти бадди")
@buddy_rate_limit(max_attempts=3, window_seconds=300)
async def cmd_find_buddy(message: Message):
    # ... existing code ...