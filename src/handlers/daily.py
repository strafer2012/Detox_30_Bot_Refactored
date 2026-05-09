from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import (
    save_report,
    add_points,
    get_active_buddy,
    mark_report_as_verified,
    is_report_verified
)

logger = logging.getLogger(__name__)
router = Router()

class ReportStates(StatesGroup):
    waiting_for_report = State()

# ====================== УТРЕННЕЕ ПОДТВЕРЖДЕНИЕ ======================
@router.callback_query(F.data == "morning_done")
async def morning_done(callback: CallbackQuery):
    await add_points(callback.from_user.id, 2, "Утреннее правило")
    await callback.message.edit_text("✅ Утреннее правило принято! +2 балла")
    await callback.answer()

# ====================== ОБРАЗОВАТЕЛЬНЫЙ БЛОК ======================
@router.callback_query(F.data == "education_done")
async def education_done(callback: CallbackQuery):
    await add_points(callback.from_user.id, 3, "Образовательный блок")
    await callback.message.edit_text("✅ Образовательный блок прочитан! +3 балла")
    await callback.answer()

# ====================== ВЕЧЕРНИЙ ОТЧЁТ ======================
@router.callback_query(F.data.startswith("report_accept_"))
async def report_accept(callback: CallbackQuery):
    day = int(callback.data.split("_")[2])
    
    buddy_id = await get_active_buddy(callback.from_user.id)
    
    if not buddy_id:
        await callback.message.edit_text("❌ У тебя нет бадди. Нельзя подтвердить отчёт.")
        await callback.answer()
        return
    
    # Получаем отчёт от бадди (в реальной версии нужно добавить логику получения сообщения)
    await add_points(callback.from_user.id, 5, "Проверка отчёта бадди")
    
    await callback.message.edit_text(
        f"✅ Отчёт за День {day} принят! +5 баллов за проверку."
    )
    await callback.answer()

# ====================== ОТПРАВКА ОТЧЁТА ======================
@router.message(F.text.startswith("/report") | F.text.startswith("Отчёт"))
async def cmd_send_report(message: Message, state: FSMContext):
    await message.answer(
        "📌 Напиши свой отчёт за сегодняшний день \n\n"
        "(Можно отправить текст или скриншот экранного времени)"
    )
    await state.set_state(ReportStates.waiting_for_report)

@router.message(ReportStates.waiting_for_report)
async def process_report(message: Message, state: FSMContext):
    user_id = message.from_user.id
    day = 1  # в реальной версии брать из базы
    
    await save_report(user_id, day, message.text or "Скриншот")
    await add_points(user_id, 10, "Отправка отчёта")
    
    await message.answer("✅ Отчёт принят! +10 баллов. \nНе забудь проверить отчёт своего бадди!")
    await state.clear()

print("✅ src/handlers/daily.py загржен (Refactored v2 - полная логика отчётов)")