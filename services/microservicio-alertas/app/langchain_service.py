import httpx
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from .config import (
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    MOCK_PRICE_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    REQUEST_TIMEOUT,
    logger,
)


class StockAlertService:
    def __init__(self):
        self.llm = self._get_llm()
        self.alert_chain = self._create_alert_chain()

    def _get_llm(self) -> BaseChatModel:
        if GOOGLE_API_KEY:
            logger.info(
                "initializing_llm",
                provider="google",
                model=GEMINI_MODEL,
            )
            return ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7,
                max_tokens=150,
            )
        elif OPENAI_API_KEY:
            logger.info(
                "initializing_llm",
                provider="openai",
                model=OPENAI_MODEL,
            )
            return ChatOpenAI(
                model=OPENAI_MODEL,
                openai_api_key=OPENAI_API_KEY,
                temperature=0.7,
                max_tokens=150,
            )
        else:
            logger.warning(
                "no_llm_configured",
                message="No hay API keys configuradas",
            )
            return None

    def _create_alert_chain(self) -> LLMChain:
        if not self.llm:
            return None

        prompt_template = """Eres un asistente de gestión de inventario profesional.

        Genera un mensaje de alerta de stock bajo que sea:
        - Profesional y conciso (2-3 líneas máximo)
        - Claro sobre la urgencia
        - Incluya información relevante del producto y precio

        Información del producto:
        - Nombre: {product_name}
        - Stock actual: {current_stock} unidades
        - Precio de proveedor sugerido: ${supplier_price}
        - ID del producto: {product_id}

        Genera solo el mensaje de alerta, sin explicaciones adicionales."""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=[
                "product_name",
                "current_stock",
                "supplier_price",
                "product_id",
            ],
        )

        return LLMChain(llm=self.llm, prompt=prompt)

    async def fetch_supplier_price(self) -> float:
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                logger.info("fetching_supplier_price", url=MOCK_PRICE_URL)
                response = await client.get(MOCK_PRICE_URL)
                response.raise_for_status()
                data = response.json()
                price = data.get("price", 99.99)
                logger.info("supplier_price_fetched", price=price)
                return float(price)
        except Exception as e:
            logger.error(
                "fetch_price_error",
                error=str(e),
                fallback_price=99.99,
            )
            return 99.99

    async def generate_alert(
        self,
        product_name: str,
        product_id: str,
        current_stock: int,
        supplier_price: float,
    ) -> str:
        if not self.alert_chain:
            # Fallback si no hay LLM configurado
            return self._generate_fallback_alert(
                product_name,
                product_id,
                current_stock,
                supplier_price,
            )

        try:
            logger.info(
                "generating_alert_with_llm",
                product_name=product_name,
                product_id=product_id,
            )

            result = await self.alert_chain.ainvoke({
                "product_name": product_name,
                "product_id": product_id,
                "current_stock": current_stock,
                "supplier_price": f"{supplier_price:.2f}",
            })

            alert_message = result["text"].strip()

            logger.info(
                "alert_generated",
                product_id=product_id,
                message_length=len(alert_message),
            )

            return alert_message

        except Exception as e:
            logger.error(
                "llm_generation_error",
                error=str(e),
                product_id=product_id,
            )
            return self._generate_fallback_alert(
                product_name,
                product_id,
                current_stock,
                supplier_price,
            )

    def _generate_fallback_alert(
        self,
        product_name: str,
        product_id: str,
        current_stock: int,
        supplier_price: float,
    ) -> str:
        return (
            f"⚠️ ALERTA DE STOCK BAJO: El producto '{product_name}' "
            f"(ID: {product_id}) tiene solo {current_stock} unidades "
            f"disponibles. Se recomienda reordenar inmediatamente. "
            f"Precio sugerido del proveedor: ${supplier_price:.2f}"
        )

    async def process_stock_alert(
        self,
        product_name: str,
        product_id: str,
        current_stock: int,
    ) -> tuple[str, float]:
        logger.info(
            "processing_stock_alert",
            product_id=product_id,
            product_name=product_name,
            current_stock=current_stock,
        )

        supplier_price = await self.fetch_supplier_price()

        alert_message = await self.generate_alert(
            product_name=product_name,
            product_id=product_id,
            current_stock=current_stock,
            supplier_price=supplier_price,
        )

        logger.info(
            "stock_alert_message",
            product_id=product_id,
            alert=alert_message,
            supplier_price=supplier_price,
        )

        print("\n" + "=" * 80)
        print("📢 ALERTA DE STOCK BAJO")
        print("=" * 80)
        print(alert_message)
        print("=" * 80 + "\n")

        return alert_message, supplier_price


alert_service = StockAlertService()
