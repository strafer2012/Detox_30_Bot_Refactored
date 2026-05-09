from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_user, get_user, update_user_timezone
import logging

logger = logging.getLogger(__name__)
router = Router()

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_goals = State()
    waiting_for_timezone = State()

# ====================== /START ======================
@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    
    if user:
        await show_main_menu(message)
    else:
        await message.answer(
            "👋 Добро пожаловать в марафон «Детокс 30»!

"
            "Давай познакомимся. Как тебя зовут?"
        )
        await state.set_state(Registration.waiting_for_name)

@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Registration.waiting_for_age)

@router.message(Registration.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Какие у тебя цели в этом марафоне?")
    await state.set_state(Registration.waiting_for_goals)

@router.message(Registration.waiting_for_goals)
async def process_goals(message: Message, state: FSMContext):
    await state.update_data(goals=message.text)
    await message.answer(
        "Укажи свой часовой пояс (например: 7 для МСК, 3 для Калининграда, -5 для Нью-Йорка и т.д.):

"
        "Если не знаешь — напиши 7"
    )
    await state.set_state(Registration.waiting_for_timezone)

@router.message(Registration.waiting_for_timezone)
async def process_timezone(message: Message, state: FSMContext):
    try:
        tz = int(message.text)
    except:
        tz = 7

    data = await state.get_data()
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=data.get("full_name"),
        timezone=tz
    )
    
    await state.clear()
    await message.answer("✅ Регистрация завершена! Добро пожаловать в марафон!")
    await show_main_menu(message)

# ====================== ГЛАВНОЕ МЕню ======================
async def show_main_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Мой прогресс", callback_data="menu_progress")],
        [InlineKeyboardButton(text="👥 Бадди", callback_data="menu_buddy")],
        [InlineKeyboardButton(text="📊 Рейтинг", callback_data="menu_rating")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
    ])
    await message.answer("🏠 Главное меню:", reply_markup=keyboard)

@router.callback_query(F.data == "menu_progress")
async def show_progress(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Сначала зарегистрируйся через /start")
        return

    text = (
        f"📅 День {user['current_day']}
"
        f"⭐ Баллы: {user['points']}
"
        f"🕒 Часовой пояс: UTC{user['timezone']:+d}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()

def back_to_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await show_main_menu(callback.message)
    await callback.answer()

print("✅ handlers/start.py загружен (Refactored v1)")