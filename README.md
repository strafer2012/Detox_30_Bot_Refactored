# Detox 30 Bot — Refactored (v2)

**Phase 10 complete** ✅

## Текущий статус
- ✅ Правильная структура
- ✅ messages.py + settings.py + Pydantic
- ✅ Улучшенное логирование + Sentry
- ✅ Admin-модули с мощными командами
- ✅ Тесты + CI/CD
- ✅ Docker Compose + Health checks + Prometheus + Grafana
- ✅ Rate limiting + spam protection

**Old repo (untouched):** https://github.com/strafer2012/Detox_30_bot

## Monitoring Stack

- **Health check**: http://localhost:8080/health
- **Prometheus**: http://localhost:9091
- **Grafana**: http://localhost:3000 (admin/admin)

## Quick Start

```bash
docker-compose up -d --build
```