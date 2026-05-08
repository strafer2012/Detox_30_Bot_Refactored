from prometheus_client import Counter, Gauge, Histogram, start_http_server
from loguru import logger

# Metrics
MESSAGES_SENT = Counter('bot_messages_sent_total', 'Total messages sent by bot')
ACTIVE_USERS = Gauge('bot_active_users', 'Number of active users')
ERRORS = Counter('bot_errors_total', 'Total errors', ['type'])
REQUEST_DURATION = Histogram('bot_request_duration_seconds', 'Request duration')


def start_prometheus_server(port: int = 9090):
    """Start Prometheus metrics server."""
    start_http_server(port)
    logger.info(f"Prometheus metrics server started on port {port}")


def update_active_users(count: int):
    ACTIVE_USERS.set(count)


def record_message_sent():
    MESSAGES_SENT.inc()


def record_error(error_type: str = "general"):
    ERRORS.labels(type=error_type).inc()