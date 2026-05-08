# Detox 30 Bot - Refactored Version

**This is the clean, refactored version of the Detox 30 Telegram Bot.**

The original repository (Detox_30_bot) remains untouched as requested.

## Project Goals
- Clean architecture
- Proper folder structure
- All bugs from v37 fixed
- Better maintainability and scalability

## Current Status
- ✅ handlers/start.py (v37) - fully fixed with proper buddy username handling and "вы" style
- ✅ database.py (v32) - improved set_buddy and get_user_id_by_username

## Planned Structure
```
detox-30-bot-refactored/
├── src/
│   ├── bot.py
│   ├── config/
│   ├── handlers/
│   ├── services/
│   ├── database/
│   └── scheduler/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Next Steps
We will gradually move and improve all files from the old project into this clean structure.

**Original repo (untouched):** https://github.com/strafer2012/Detox_30_bot