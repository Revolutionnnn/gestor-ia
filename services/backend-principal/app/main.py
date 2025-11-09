from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_ORIGINS, PORT, logger
from .database import Base, engine
from .routes import health, products

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Backend Principal",
    version="1.0.0",
    description="API principal para gestión de productos con IA",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(products.router)


@app.on_event("startup")
async def startup_event():
    logger.info("service_starting", service="backend-principal", port=PORT)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("service_shutdown", service="backend-principal")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)
