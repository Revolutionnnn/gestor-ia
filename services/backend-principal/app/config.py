import os

import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres_password@postgres:5432/ecommerce_db",
)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(
    ","
)
PORT = int(os.getenv("PORT", 8000))
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", 10))
ALERTS_SERVICE_URL = os.getenv(
    "ALERTS_SERVICE_URL",
    "http://microservicio-alertas:8002",
)
ALERTS_WEBHOOK_TIMEOUT = int(os.getenv("ALERTS_WEBHOOK_TIMEOUT", 10))
AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://microservicio-auth:8001",
)
