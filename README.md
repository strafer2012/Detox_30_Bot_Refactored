# Detox 30 Bot — Refactored (v2)

**admin.py разделён на модули** ✅

## Текущая структура
```
src/admin/
├── __init__.py
├── router.py              # главный роутер + /adminhelp
├── commands/
│   ├── user_management.py   # /setday, /settz, /ban...
│   ├── messaging.py         # /force_message, /replay...
│   ├── stats.py             # /stats, /active...
│   └── settings.py          # /settime, /pause...
└── utils.py
```

**Phase 2 complete.** Дальше — перенос остальных файлов и улучшения.