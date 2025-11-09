from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS, PORT, LOG_LEVEL, OPENAI_MODEL, logger
from routes import router
from llm_service import llm_service


app = FastAPI(
    title="Microservicio IA",
    description="Servicio especializado en generación de contenido con LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return {
        "error": "internal_server_error",
        "message": "Ocurrió un error inesperado",
        "detail": str(exc) if LOG_LEVEL == "DEBUG" else None
    }


@app.on_event("startup")
async def startup_event():
    logger.info(
        "service_starting",
        service="microservicio-ia",
        port=PORT,
        model=OPENAI_MODEL,
        llm_configured=llm_service.is_configured()
    )


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("service_shutdown", service="microservicio-ia")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level=LOG_LEVEL.lower()
    )
