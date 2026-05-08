from aiogram import Router, F

router = Router()

@router.message(F.text == "Отчёт")
async def cmd_report(message):
    await message.answer("📊 Отчёт принят! Спасибо!")

print('✅ handlers/daily.py loaded with router')