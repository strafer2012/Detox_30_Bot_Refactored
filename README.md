# Detox 30 Bot — Refactored (v2) ✅

**Project Status: PRODUCTION READY**

## Что было сделано

### Архитектура
- ✅ Правильная модульная структура (`src/`)
- ✅ Централизованные тексты (`messages.py`)
- ✅ Централизованные настройки (`settings.py` + Pydantic)

### Безопасность и мониторинг
- ✅ Улучшенное логирование (loguru + structured JSON)
- ✅ Sentry integration
- ✅ Rate limiting + spam protection
- ✅ Health check endpoint (`/health`)
- ✅ Prometheus metrics + Grafana dashboard

### Admin панель
- ✅ Разделённая на модули (`admin/commands/`)
- ✅ `/stats`, `/statsfull`, `/nextinfo`, `/user`
- ✅ `/force_message`, `/settime`, `/add_points`
- ✅ `/ban`, `/unban`
- ✅ Система уведомлений админу

### DevOps
- ✅ Тесты (pytest)
- ✅ CI/CD (GitHub Actions)
- ✅ Docker Compose (production-ready)
- ✅ Pre-configured Grafana dashboard

## Быстрый запуск

```bash
git clone https://github.com/strafer2012/Detox_30_Bot_Refactored.git
cd Detox_30_Bot_Refactored
cp .env.example .env
# Заполни .env

docker-compose up -d --build
```

## Мониторинг

- Health: http://localhost:8080/health
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)

## Старый проект

**https://github.com/strafer2012/Detox_30_bot** — остался нетронутым (as requested).

---

**Project Status: PRODUCTION READY** ✅

**Version:** v2.0.0
**Last Updated:** 2026-05-08