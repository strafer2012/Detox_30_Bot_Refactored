import time
from collections import defaultdict
from functools import wraps

from aiogram.types import Message

# In-memory rate limiter (for production use Redis)
user_message_times = defaultdict(list)


def rate_limit(max_messages: int = 5, window_seconds: int = 60):
    """Decorator to limit messages per user."""
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_id = message.from_user.id
            now = time.time()
            
            # Clean old timestamps
            user_message_times[user_id] = [
                t for t in user_message_times[user_id] 
                if now - t < window_seconds
            ]
            
            if len(user_message_times[user_id]) >= max_messages:
                await message.answer(
                    "⚠️ Слишком много сообщений. Пожалуйста, подождите немного минут."
                )
                return
            
            user_message_times[user_id].append(now)
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator


# Spam protection for buddy selection
buddy_selection_times = defaultdict(list)

def buddy_rate_limit(max_attempts: int = 3, window_seconds: int = 300):
    """Limit buddy selection attempts."""
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_id = message.from_user.id
            now = time.time()
            
            buddy_selection_times[user_id] = [
                t for t in buddy_selection_times[user_id]
                if now - t < window_seconds
            ]
            
            if len(buddy_selection_times[user_id]) >= max_attempts:
                await message.answer(
                    "⚠️ Слишком много попыток выбрать бадди. Подождите 5 минут."
                )
                return
            
            buddy_selection_times[user_id].append(now)
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator