from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import aiosqlite

from config.settings import DATABASE_PATH, ADMIN_ID

router = Router()

# ... (rest of the file remains the same) ...