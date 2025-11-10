import os

import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

PORT = int(os.getenv("PORT", "8002"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
MOCK_PRICE_URL = os.getenv("MOCK_PRICE_URL", "https://dummyjson.com/products/1")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:8000,http://localhost:3000",
).split(",")

if not OPENAI_API_KEY and not GOOGLE_API_KEY:
    logger.warning("no_api_keys_configured", message="Se recomienda configurar OPENAI_API_KEY o GOOGLE_API_KEY")
