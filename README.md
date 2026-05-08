# Detox 30 Bot — Refactored (v2)

**Phase 6 complete** ✅

## Текущий статус
- ✅ Правильная структура
- ✅ messages.py + settings.py + Pydantic
- ✅ Улучшенное логирование
- ✅ Admin-модули с мощными командами
- ✅ Тесты (pytest)
- ✅ GitHub Actions (CI/CD)
- ✅ Docker Compose (production-ready deploy)

**Old repo (untouched):** https://github.com/strafer2012/Detox_30_bot

## Запуск (Production)

```bash
git clone https://github.com/strafer2012/Detox_30_Bot_Refactored.git
cd Detox_30_Bot_Refactored
cp .env.example .env
# Заполни .env файл

docker-compose up -d --build
```

Логи: `docker-compose logs -f bot`