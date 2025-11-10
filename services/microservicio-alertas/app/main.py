from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_ORIGINS, PORT, logger
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "service_starting",
        service="microservicio-alertas",
        port=PORT,
    )
    yield
    logger.info("service_shutdown", service="microservicio-alertas")


app = FastAPI(
    title="Microservicio de Alertas de Stock",
    description="Servicio automatizado para procesar alertas de stock bajo usando LangChain",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="", tags=["alertas"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
    )
