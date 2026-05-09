from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
from database import (
    save_report, get_buddy, get_user, add_points,
    create_report, mark_report_as_verified, is_report_verified,
    has_active_buddy
)
import logging

logger = logging.getLogger(__name__)
router = Router()

# ====================== УТРЕННЕЕ СООБЩЕНИЕ С КНОПКОЙ ======================
async def send_morning_message_with_button(bot, user_id: int, day: int, text: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принято", callback_data="morning_done")]
    ])
    try:
        await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="HTML")
        logger.info(f"Утреннее сообщение с кнопкой отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки утреннего сообщения {user_id}: {e}")


# ====================== ОБРАЗОВАТЕЛЬНОЕ СООБЩЕНИЕ С КНОПКОЙ ======================
async def send_education_message_with_button(bot, user_id: int, day: int, text: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принято", callback_data="education_done")]
    ])
    try:
        await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="HTML")
        logger.info(f"Образовательное сообщение с кнопкой отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка отправки образовательного сообщения {user_id}: {e}")


# ====================== ОБРАБОТЧИК КНОПКИ "✅ ПРИНЯТО" (УТРО) ======================
@router.callback_query(F.data == "morning_done")
async def morning_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        await add_points(user_id, 2, reason="morning_confirmed")
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ Отмечено +2 балла",
            reply_markup=None
        )
        await callback.answer("Вы получили +2 балла! ✅", show_alert=False)
        logger.info(f"Пользователь {user_id} подтвердил утреннее сообщение (+2 балла)")
    except Exception as e:
        logger.error(f"Ошибка в morning_done: {e}")
        await callback.answer("Ошибка при начислении баллов", show_alert=True)


# ====================== ОБРАБОТЧИК КНОПКИ "✅ ПРИНЯТО" (ОБРАЗОВАНИЕ) ======================
@router.callback_query(F.data == "education_done")
async def education_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        await add_points(user_id, 2, reason="education_confirmed")
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ Отмечено +2 балла",
            reply_markup=None
        )
        await callback.answer("Вы получили +2 балла! ✅", show_alert=False)
        logger.info(f"Пользователь {user_id} подтвердил образовательное сообщение (+2 балла)")
    except Exception as e:
        logger.error(f"Ошибка в education_done: {e}")
        await callback.answer("Ошибка при начислении баллов", show_alert=True)


# ====================== ВЕЧЕРНЕЕ СООБЩЕНИЕ С ОДНОЙ КНОПКОЙ (ОБНОВЛЕНО) ======================
async def send_evening_message_with_buttons(bot, user_id: int, day: int, text: str):
    """Обновлённая версия: проверяет наличие бадди и использует правильный текст кнопки"""
    has_buddy = await has_active_buddy(user_id)
    
    if has_buddy:
        button_text = "✅ Отчёт от бадди принял"
        callback_data = f"report_accept_{day}"
    else:
        button_text = "👥 Выберите себе бадди"
        callback_data = "menu_buddy"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, callback_data=callback_data)]
    ])
   
    try:
        await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode="HTML")
        logger.info(f"[Evening] Сообщение с кнопкой отправлено пользователю {user_id} (День {day}, бадди: {has_buddy})")
    except Exception as e:
        logger.error(f"Ошибка отправки вечернего сообщения {user_id}: {e}")


# ====================== ОБРАБОТЧИК КНОПКИ "✅ ОТЧЁТ ОТ БАДДИ ПРИНЯЛ" ======================
@router.callback_query(F.data.startswith("report_accept_"))
async def handle_report_accept(callback: CallbackQuery):
    receiver_id = callback.from_user.id
    try:
        day = int(callback.data.split("_")[2])
       
        # Получаем ID отправителя отчёта (его бадди)
        sender_id = await get_buddy(receiver_id)
       
        if sender_id:
            await add_points(sender_id, 5, reason="report_verified_by_buddy")
           
            try:
                await callback.bot.send_message(
                    sender_id,
                    f"✅ Ваш бадди принял ваш отчёт за День {day}!\n"
                    f"Вам зачислено +5 баллов."
                )
            except Exception as send_err:
                logger.error(f"Не удалось отправить уведомление {sender_id}: {send_err}")
        else:
            logger.warning(f"У {receiver_id} нет бадди при нажатии 'Отчёт принял'")
       
        # Полностью убираем клавиатуру
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("✅ Спасибо! Отчёт принят.", show_alert=True)
       
    except Exception as e:
        logger.error(f"Ошибка в handle_report_accept: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ====================== ОСТАЛЬНЫЕ ФУНКЦИИ (ОТЧЁТЫ) ======================
@router.message(F.text == "📊 Отправить отчёт")
async def cmd_send_report(message: Message):
    user_id = message.from_user.id
    stats = await get_user(user_id)
    current_day = stats["current_day"] if stats else 1
   
    quick_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выполнено + Хорошо", callback_data=f"quick_report_{current_day}_done_good")],
        [InlineKeyboardButton(text="Выполнено + Нормально", callback_data=f"quick_report_{current_day}_done_ok")],
        [InlineKeyboardButton(text="Не выполнено + Сложно", callback_data=f"quick_report_{current_day}_not_hard")],
        [InlineKeyboardButton(text="Прикрепить скриншот", callback_data=f"report_screen_{current_day}")]
    ])
   
    await message.answer(
        f"Отправка отчёта за День {current_day}\n\n"
        f"Выберите быстрый вариант или прикрепите скриншот:",
        reply_markup=quick_keyboard
    )


@router.callback_query(F.data.startswith("report_"))
async def handle_report_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
   
    if data.startswith("report_screen_"):
        day = int(data.split("_")[2])
        await callback.message.answer(
            f"Отправьте скриншот «Экранного времени» за День {day}\n\n"
            f"После отправки напишите текст отчёта."
        )
        await callback.answer()
   
    elif data.startswith("quick_report_"):
        parts = data.split("_")
        day = int(parts[2])
        status = parts[3]
       
        status_text = {
            "done_good": "Выполнено + Хорошо",
            "done_ok": "Выполнено + Нормально",
            "not_hard": "Не выполнено + Сложно"
        }.get(status, "Выполнено")
       
        report_text = f"День {day} — {status_text}"
       
        report_id = await create_report(user_id, day, report_text)
        await add_points(user_id, 5, reason="report_submitted")
       
        buddy_id = await get_buddy(user_id)
        if buddy_id:
            sender_username = callback.from_user.username or f"ID {user_id}"
            # Здесь можно добавить вызов add_report_verification_button если есть
            await callback.bot.send_message(
                buddy_id,
                f"📨 Ваш бадди @{sender_username} отправил отчёт за День {day}:\n\n{report_text}"
            )
       
        await callback.message.edit_text("✅ Отчёт сохранён! Ваш бадди получил уведомление.")
        await callback.answer()


@router.callback_query(F.data.startswith("verify_report_"))
async def handle_report_verification(callback: CallbackQuery):
    report_id = int(callback.data.split("_")[2])
    verifier_id = callback.from_user.id
   
    if await is_report_verified(report_id):
        await callback.answer("Этот отчёт уже был подтверждён.", show_alert=True)
        return
   
    sender_id = await mark_report_as_verified(report_id, verifier_id)
   
    if sender_id:
        await add_points(sender_id, 5, reason="report_verified_by_buddy")
       
        try:
            await callback.bot.send_message(
                sender_id,
                "✅ Ваш бадди подтвердил получение вашего отчёта! +5 бонусных баллов."
            )
        except:
            pass
       
        await callback.message.edit_text("✅ Спасибо! Отчёт подтверждён.")
        await callback.answer()
    else:
        await callback.answer("Ошибка. Отчёт не найден.", show_alert=True)


@router.message(lambda m: m.text and m.text.startswith("День") and "отчёт" in m.text.lower())
async def handle_report(message: Message):
    user_id = message.from_user.id
    text = message.text
   
    try:
        day = int(text.split()[1])
    except:
        day = 1
   
    report_id = await create_report(user_id, day, text)
    await add_points(user_id, 5, reason="report_submitted")
   
    buddy_id = await get_buddy(user_id)
    if buddy_id:
        sender_username = message.from_user.username or f"ID {user_id}"
        await message.bot.send_message(
            buddy_id,
            f"📨 Ваш бадди @{sender_username} отправил отчёт за День {day}:\n\n{text}"
        )
   
    await message.answer("✅ Отчёт сохранён! Ваш бадди получил уведомление.")


print("✅ daily.py загружен — обновлён под новую логику вечера с проверкой бадди + улучшенная защита")
