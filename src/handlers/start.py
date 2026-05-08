from aiogram import Router, F

from config.messages import (
    START_WELCOME,
    START_1_REPLY,
    BUDDY_SELECTED_TEXT,
    BUDDY_REQUEST_SENT,
    TIMEZONE_SAVED,
    ERROR_BUDDY_SELF,
    ERROR_BUDDY_ALREADY_HAS,
    ERROR_BUDDY_NOT_FOUND,
)

from config.settings import ADMIN_ID, CLOSED_CHAT_LINK

from database.database import get_user_id_by_username, set_buddy, add_points

import aiosqlite

router = Router()

# ... (rest of the file - the actual handlers code)

print('✅ handlers/start.py loaded with real imports')