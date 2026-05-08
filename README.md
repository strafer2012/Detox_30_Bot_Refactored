# Detox 30 Bot — Refactored (v2)

**Phase 7 complete** ✅

## Текущий статус
- ✅ Правильная структура
- ✅ messages.py + settings.py + Pydantic
- ✅ Улучшенное логирование + Sentry
- ✅ Admin-модули с мощными командами
- ✅ Тесты (pytest) + CI/CD
- ✅ Docker Compose (production-ready)
- ✅ Sentry + Uptime monitoring recommendations

**Old repo (untouched):** https://github.com/strafer2012/Detox_30_bot

## Запуск

```bash
docker-compose up -d --build
```

## Мониторинг (recommended)

1. **Sentry** — уже настроен в коде
2. **Uptime checks** — настрой UptimeRobot / BetterStack / self-hosted
3. **Health check** — добавь простой HTTP endpoint или пинг каждые 5 минут