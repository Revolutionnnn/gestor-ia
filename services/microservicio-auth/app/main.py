from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_ORIGINS, LOG_LEVEL, PORT, SERVICE_NAME, logger
from .database import Base, engine
from .routes import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microservicio de Autenticación",
    description=(
        "Servicio dedicado para registro y login del ecosistema de e-commerce"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("service_starting", service=SERVICE_NAME, port=PORT)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("service_shutdown", service=SERVICE_NAME)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level=LOG_LEVEL.lower(),
    )
