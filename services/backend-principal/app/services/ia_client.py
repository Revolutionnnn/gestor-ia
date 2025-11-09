import httpx
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

IA_SERVICE_URL = os.getenv("IA_SERVICE_URL", "http://microservicio-ia:8001")
TIMEOUT = int(os.getenv("TIMEOUT_IA_SERVICE", 35))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def generate_description(name: str, keywords: list) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{IA_SERVICE_URL}/generate/description",
            json={"name": name, "keywords": keywords}
        )
        response.raise_for_status()
        return response.json()["generated_description"]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def generate_category(product_name: str, description: str) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{IA_SERVICE_URL}/generate/category",
            json={"product_name": product_name, "description": description}
        )
        response.raise_for_status()
        return response.json()["suggested_category"]
