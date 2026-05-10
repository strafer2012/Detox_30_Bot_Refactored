# Detox 30 Bot - Refactored (v42)

**Цифровой Детокс 30 дней** — Telegram-бот с системой бадди, ежедневными образовательными сообщениями, рейтингом, оплатой через Tribute и полной поддержкой часовых поясов пользователей.

## 🚀 Возможности

- **30-дневная программа** с утренними (08:00), образовательными (14:00) и вечерними (20:30) сообщениями по локальному времени пользователя
- **Система бадди** — поиск, запросы, принятие/отклонение, история, взаимные отчёты (+5 баллов за проверку)
- **Рейтинг и баллы** — за прохождение дней, отчёты, проверки бадди
- **Админ-панель** — статистика, начисление баллов, принудительные сообщения, смена часового пояса
- **Мониторинг** — Health check (порт 8080), Prometheus metrics (порт 9090)
- **Защита от дубликатов** сообщений
- **Sentry** интеграция для ошибок
- **Graceful shutdown** и Railway-оптимизации

## 📦 Структура проекта

```
.
├── src/
│   ├── bot.py                 # Точка входа
│   ├── config/
│   │   ├── settings.py        # Pydantic env vars
│   │   ├── logging.py         # loguru + Sentry
│   │   └── messages.py        # Константы текстов
│   ├── database/
│   │   └── database.py        # aiosqlite + buddy/reports
│   ├── handlers/
│   │   ├── start.py           # Регистрация, FSM
│   │   ├── daily.py           # Отчёты
│   │   ├── buddy.py           # Бадди-система
│   │   ├── main_menu.py       # Главное меню
│   │   └── admin.py           # Админ-команды
│   ├── scheduler/
│   │   └── scheduler.py       # Universal Local Time Scheduler v7.6
│   ├── monitoring/
│   │   ├── health_server.py
│   │   └── metrics.py
│   ├── utils/
│   │   └── rate_limiter.py
│   ├── admin/                 # Расширенные админ-роутеры
│   └── free_course.py / paid_course.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── .env.example
├── .github/workflows/ci.yml
└── README.md
```

## 🚀 Быстрый старт (локально)

1. **Клонируйте репозиторий**
   ```bash
   git clone <repo-url>
   cd Detox_30_Bot_Refactored
   ```

2. **Создайте .env**
   ```bash
   cp .env.example .env
   # Отредактируйте .env — вставьте BOT_TOKEN и ADMIN_ID
   ```

3. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите бота**
   ```bash
   PYTHONPATH=src python src/bot.py
   # или просто: python src/bot.py
   ```

Бот автоматически создаст БД `detox30.db`, таблицы и начнёт отправку сообщений по расписанию.

## 🐳 Docker / Docker Compose

```bash
# Сборка и запуск
docker-compose up -d --build

# Логи
docker-compose logs -f bot

# Мониторинг
# Health: http://localhost:8080/health
# Prometheus: http://localhost:9091
```

**Переменные в .env** (см. `.env.example`):
- `BOT_TOKEN` (обязательно)
- `ADMIN_ID` (обязательно)
- `SENTRY_DSN` (опционально)
- `DATABASE_PATH`, времена, таймзона и т.д.

## 🔄 CI/CD

GitHub Actions автоматически:
- Линтит код (black)
- Проверяет типы (mypy)
- Проверяет синтаксис всех .py файлов
- Тестирует импорты
- Собирает Docker-образ

Workflow: `.github/workflows/ci.yml`

## 📝 Разработка

- **Форматирование**: `black src/`
- **Типизация**: `mypy src/ --ignore-missing-imports`
- **Тесты**: (добавите pytest в будущем)
- **Логи**: `logs/bot_YYYY-MM-DD.log` (JSON)

## 🌍 Часовые пояса

Бот использует **локальное время пользователя** (из БД `timezone`).
- По умолчанию UTC+7
- Админ может менять через `/settime <id> <offset>`
- Проверка каждую минуту, отправка точно в 08:00 / 14:00 / 20:30 / 21:00 по времени пользователя

## 📊 Мониторинг

- **Health Server**: порт 8080 — `/health`
- **Prometheus**: порт 9090 — `/metrics` (сообщения, пользователи, ошибки)
- В docker-compose поднят отдельный Prometheus на 9091

## 🛡️ Безопасность

- Rate limiting на сообщения и выбор бадди
- Защита от дубликатов отправки (таблица `sent_messages`)
- Admin-only команды
- Graceful shutdown по SIGTERM/SIGINT

## 📈 Версия

**2026-05-10-v42-full-handlers-connected**

Полная миграция в `src/` структуру, все хендлеры подключены, scheduler v7.6 с защитой от дубликатов, локальное время, buddy-система, админка, мониторинг.

---

**Удачи в марафоне!** 💪

Если бот упадёт — проверьте логи и `.env`.
