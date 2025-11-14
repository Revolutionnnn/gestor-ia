import logging
import os
from typing import List

import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

SERVICE_NAME = "microservicio-auth"
PORT = int(os.getenv("PORT", os.getenv("AUTH_SERVICE_PORT", 8003)))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DATABASE_URL = os.getenv(
    "AUTH_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres_password@postgres:5432/ecommerce_db",
    ),
)
JWT_SECRET_KEY = os.getenv("AUTH_JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("AUTH_JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)
REFRESH_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("AUTH_REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)
)
PASSWORD_MIN_LENGTH = int(os.getenv("AUTH_PASSWORD_MIN_LENGTH", 8))
ALLOWED_ORIGINS: List[str] = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:8000",
).split(",")

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))

if JWT_SECRET_KEY == "change-me":
    logger.warning(
        "weak_jwt_secret",
        detail="Provide AUTH_JWT_SECRET in production",
    )
