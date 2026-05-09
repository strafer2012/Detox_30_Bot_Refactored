from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import logging

from database import (
    add_user, get_user, update_user_timezone, 
    get_user_progress, get_rating_report,
    get_active_buddy, get_buddy_username, get_buddy_days_together
)

logger = logging.getLogger(__name__)
router = Router()

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_timezone = State()


# ====================== /START И РЕГИСТРАЦИЯ ======================
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if user:
        await state.clear()
        await show_main_menu(message)
    else:
        await message.answer(
            "👋 Добро пожаловать в марафон «Детокс 30»!\n\n"
            "Это 30-дневный челлендж по восстановлению дофаминовой системы и контролю экранного времени.\n\n"
            "Давай познакомимся! Как тебя зовут (полное имя)?"
        )
        await state.set_state(Registration.waiting_for_name)


@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Пожалуйста, введи настоящее имя:")
        return
    
    await state.update_data(full_name=name)
    await message.answer(
        f"Отлично, {name}!\n\n"
        "Теперь укажи свой часовой пояс в формате UTC (целое число):\n"
        "• 7 — Москва / СПб\n"
        "• 3 — Калининград\n"
        "• 5 — Екатеринбург\n"
        "• 8 — Новосибирск / Омск\n"
        "• 9 — Владивосток\n"
        "• 10 — Магадан\n"
        "• 12 — Камчатка\n\n"
        "Для других стран: -5 Нью-Йорк, 0 Лондон, 1 Париж, 8 Пекин и т.д.\n\n"
        "Если не уверен — напиши 7"
    )
    await state.set_state(Registration.waiting_for_timezone)


@router.message(Registration.waiting_for_timezone)
async def process_timezone(message: Message, state: FSMContext):
    try:
        tz = int(message.text.strip())
        if tz < -12 or tz > 14:
            raise ValueError
    except:
        await message.answer("Неверный формат. Введи число от -12 до 14 (например 7):")
        return
    
    data = await state.get_data()
    full_name = data.get("full_name")
    username = message.from_user.username
    
    await add_user(
        user_id=message.from_user.id,
        username=username,
        full_name=full_name
    )
    await update_user_timezone(message.from_user.id, tz)
    
    await state.clear()
    
    await message.answer(
        "✅ Регистрация успешно завершена!\n\n"
        f"Имя: {full_name}\n"
        f"Часовой пояс: UTC{tz:+d}\n\n"
        "Теперь ты участник марафона! Каждый день в 08:00, 14:00 и 20:30 ты будешь получать задания и напоминания.\n\n"
        "Удачи! 💪"
    )
    await show_main_menu(message)


# ====================== ГЛАВНОЕ МЕНЮ ======================
def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="menu_progress")],
        [InlineKeyboardButton(text="👥 Бадди-система", callback_data="menu_buddy")],
        [InlineKeyboardButton(text="🏆 Общий рейтинг", callback_data="menu_rating")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
        [InlineKeyboardButton(text="💳 Оплатить марафон (999₽)", callback_data="pay_marathon")],
        [InlineKeyboardButton(text="📢 Пригласить друга", callback_data="invite_friend")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")],
    ])


async def show_main_menu(message: Message):
    await message.answer(
        "🏠 Главное меню марафона «Детокс 30»",
        reply_markup=get_main_menu_keyboard()
    )


# ====================== CALLBACKS МЕНЮ ======================
@router.callback_query(F.data == "menu_progress")
async def menu_progress(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    progress = await get_user_progress(user_id)
    
    if not user or not progress:
        await callback.answer("Сначала пройди регистрацию через /start", show_alert=True)
        return
    
    tz = user.get("timezone", 7)
    buddy_status = "✅ Есть (дней вместе: {})".format(progress.get("buddy_days", 0)) if progress.get("buddy_id") else "❌ Нет бадди"
    paid = "✅ Оплачен" if user.get("is_paid") else "🆓 Бесплатный участник"
    
    text = (
        f"📊 <b>Твой прогресс</b>\n\n"
        f"📅 День марафона: <b>{progress['current_day']}/30</b>\n"
        f"⭐ Баллы: <b>{progress['points']}</b>\n"
        f"👥 Бадди: {buddy_status}\n"
        f"🕒 Часовой пояс: <b>UTC{tz:+d}</b>\n"
        f"💳 Статус: {paid}\n\n"
        f"Продолжай в том же духе! Каждый день — шаг к свободе от дофаминовой зависимости."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "menu_buddy")
async def menu_buddy(callback: CallbackQuery):
    user_id = callback.from_user.id
    active_buddy = await get_active_buddy(user_id)
    
    if active_buddy:
        buddy_name = await get_buddy_username(active_buddy)
        days = await get_buddy_days_together(user_id)
        text = (
            f"👥 <b>Твой бадди</b>\n\n"
            f"Имя: <b>{buddy_name}</b>\n"
            f"Дней вместе: <b>{days}</b>\n\n"
            "Вы поддерживаете друг друга каждый день!\n"
            "Проверяйте отчёты друг друга и получайте +5 баллов за проверку."
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Разорвать связь с бадди", callback_data="break_buddy")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
        ])
    else:
        text = (
            "👥 <b>Бадди-система</b>\n\n"
            "У тебя пока нет бадди.\n\n"
            "Бадди — это партнёр по марафону, который помогает не сдаваться.\n"
            "Вы будете проверять отчёты друг друга и получать бонусные баллы!\n\n"
            "Выбери бадди из списка или пригласи друга."
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Найти бадди", callback_data="find_buddy")],
            [InlineKeyboardButton(text="📩 Пригласить своего друга", callback_data="invite_buddy")],
            [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
        ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "menu_rating")
async def menu_rating(callback: CallbackQuery):
    top = await get_rating_report(10)
    
    text = "🏆 <b>Топ-10 участников марафона</b>\n\n"
    for i, (uid, name, pts, day, paid) in enumerate(top, 1):
        name = name or f"ID {uid}"
        paid_mark = "💳" if paid else ""
        text += f"{i}. {name} — {pts} баллов (день {day}) {paid_mark}\n"
    
    text += "\nТы можешь подняться выше! Продолжай ежедневно выполнять задания."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    tz = user.get("timezone", 7) if user else 7
    
    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"🕒 Текущий часовой пояс: <b>UTC{tz:+d}</b>\n\n"
        "Здесь ты можешь изменить часовой пояс (чтобы сообщения приходили в удобное время).\n\n"
        "Также скоро появятся уведомления и другие настройки."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕒 Изменить часовой пояс", callback_data="change_timezone")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "pay_marathon")
async def pay_marathon(callback: CallbackQuery):
    text = (
        "💳 <b>Оплата марафона</b>\n\n"
        "Полная версия марафона стоит 999₽.\n\n"
        "Что даёт оплата:\n"
        "• Доступ ко всем материалам и заданиям\n"
        "• Персональные рекомендации\n"
        "• Приоритетная поддержка\n"
        "• Сертификат об окончании\n\n"
        "Оплата через Tribute (ссылка будет в боте после нажатия)."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить 999₽", callback_data="pay_now")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    text = (
        "📢 <b>Пригласить друга</b>\n\n"
        "Поделись ссылкой на бота с друзьями:\n"
        "https://t.me/Detox_30_bot?start=ref_{}\n\n"
        "Когда твой друг зарегистрируется по твоей ссылке — ты получишь +50 бонусных баллов!\n\n"
        "Чем больше друзей — тем выше ты в рейтинге и тем эффективнее марафон."
    ).format(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    text = (
        "🆘 <b>Поддержка</b>\n\n"
        "Если у тебя возникли вопросы, проблемы с ботом или нужна помощь — напиши сюда:\n\n"
        "Просто отправь сообщение в чат, и мы ответим в течение 24 часов.\n\n"
        "Также ты можешь написать @strafer2012 напрямую."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Главное меню марафона «Детокс 30»",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


# ====================== ЗАГЛУШКИ ДЛЯ БУДУЩИХ ФУНКЦИЙ ======================
@router.callback_query(F.data == "change_timezone")
async def change_timezone(callback: CallbackQuery):
    await callback.answer(
        "Изменение часового пояса будет доступно в следующей версии. Пока напиши /start заново и укажи новый при регистрации.",
        show_alert=True
    )


# ====================== ДРУГИЕ CALLBACKS (ЗАГЛУШКИ) ======================
@router.callback_query(F.data.in_({"find_buddy", "invite_buddy", "break_buddy", "pay_now"}))
async def placeholder_callbacks(callback: CallbackQuery):
    await callback.answer("Эта функция будет доступна в следующей версии бота! 🚀", show_alert=True)


print("✅ start.py загружен — регистрация, FSM, главное меню и все callbacks готовы")