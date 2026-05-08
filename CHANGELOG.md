# Changelog

## [2.0.0] - 2026-05-08

### Added
- Complete project restructure (`src/`)
- Centralized messages and settings (Pydantic)
- Full admin panel with modular commands
- Rate limiting and spam protection
- Health check endpoint + Prometheus metrics
- Grafana dashboard
- Comprehensive test suite (pytest)
- GitHub Actions CI/CD
- Docker Compose with monitoring stack
- Sentry integration

### Changed
- All handlers updated to use centralized messages
- Admin commands split into logical modules
- Improved logging with structured JSON

### Security
- Rate limiting on critical endpoints
- Buddy selection protection
- Input validation

**Status:** Production Ready