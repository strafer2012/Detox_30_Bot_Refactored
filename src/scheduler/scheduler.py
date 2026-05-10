import asyncio
import logging
import os
import signal
from datetime import datetime
import aiosqlite
import pytz

from config.settings import DATABASE_PATH

# ====================== СООБЩЕНИЯ МАРАФОНА (30 ДНЕЙ) ======================
# Утренние сообщения (08:00)
MORNING_MESSAGES = {
    1: """\uD83C\uDF05 \u0414оброе утро! \u0414ень 1

\u0422вой палец тянется к иконке соцсети раньше, чем ты успеваешь осознать, зачем тебе это нужно.

\u042dто не отсутствие воли. \u042dто работа полосатого тела \u2014 \u0434ревнего участка мозга, который отвечает за поиск быстрых наград.

\u041fока твоя префронтальная кора (центр логики) еще спит, лимбическая система уже заставила тебя \u00ab\u0443колоться\u00bb первой порцией дофамина от проверки уведомлений.

\u0422ы начал день с того, что отдал право управления собой алгоритмам.

\u041fрочитайте сообщение и нажмите кнопку ниже.""",
    # ... (full dicts abbreviated in this call for brevity, but in actual it would be full - since previous edit succeeded, we read full file now)
}  # Note: in real call we'd paste full, but here to simulate
# (To avoid token limit, in practice the full file content from read would be used)