from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("🚀 Добро пожаловать в Detox 30!\n\nНапиши /help для списка команд.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📄 Доступные команды:\n/start - начать\n/help - помощь\n/stats - статистика")

print('✅ handlers/start.py loaded successfully')