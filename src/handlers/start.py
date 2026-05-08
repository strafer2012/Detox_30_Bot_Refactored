from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "🚀 Добро пожаловать в Detox 30!\n\n"
        "Это марафон по цифровому детоксу на 30 дней.\n\n"
        "🕐 Расписание:\n"
        "• 08:00 — утреннее правило\n"
        "• 14:00 — образовательный блок\n"
        "• 20:30 — вечерний отчёт\n\n"
        "Нажмите кнопку ниже, чтобы настроить часовой пояс."
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Настроить часовой пояс", callback_data="set_timezone")]
        ]
    )
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "set_timezone")
async def set_timezone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌍 Выберите ваш часовой пояс:\n\n"
        "Например: 3 (Москва), 7 (Красноярск), 10 (Владивосток)"
    )
    await state.set_state("waiting_timezone")
    await callback.answer()

@router.message(F.text.regexp(r"^-?\d{1,2}$"))
async def process_timezone(message: Message, state: FSMContext):
    try:
        tz = int(message.text)
        if not -12 <= tz <= 14:
            raise ValueError
        
        # TODO: сохранить в базу
        await message.answer(
            f"✅ Часовой пояс UTC+{tz} сохранён!\n\n"
            "Теперь выберите бадди \u0438 начните марафон!"
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Неверный часовой пояс. Введите число от -12 до 14.")

print('✅ handlers/start.py loaded with Day 0 welcome chain')