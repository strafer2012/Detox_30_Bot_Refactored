# Detox 30 Bot — Refactored (v2)

**Clean architecture version** (старый репозиторий оставлен без изменений)

## ✅ Что уже сделано
- ✅ Правильная структура проекта
- ✅ handlers/start.py v37 (все баги исправлены)
- ✅ database.py v32 (set_buddy и get_user_id_by_username улучшены)
- ✅ bot.py и scheduler.py перенесены и легко чищены

## Структура проекта
```
src/
├── bot.py
├── config/
│   ├── settings.py
│   └── messages.py          # все тексты бота
├── handlers/
│   ├── start.py             # v37
│   └── daily.py
├── services/
│   ├── buddy_service.py
│   └── points_service.py
├── database/
│   └── database.py          # v32
├── scheduler/
│   └── scheduler.py
└── utils/

.env.example
requirements.txt
Dockerfile
```

## Следующие шаги
1. Перенести все остальные файлы из старого проекта
2. Разделить admin.py на несколько модулей
3. Добавить .env + pydantic
4. Улучшить логирование и error handling

**Ссылка на старый проект (без изменений):** https://github.com/strafer2012/Detox_30_bot