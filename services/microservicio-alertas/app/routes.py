from fastapi import APIRouter, HTTPException, status

from .config import logger
from .langchain_service import alert_service
from .models import AlertResponse, HealthResponse, StockAlertWebhook

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="microservicio-alertas",
    )


@router.post("/webhook/stock-alert", response_model=AlertResponse)
async def stock_alert_webhook(webhook_data: StockAlertWebhook):
    try:
        logger.info(
            "webhook_received",
            product_id=webhook_data.product_id,
            product_name=webhook_data.product_name,
            current_stock=webhook_data.current_stock,
        )

        # Procesar la alerta usando LangChain
        alert_message, supplier_price = await alert_service.process_stock_alert(
            product_name=webhook_data.product_name,
            product_id=webhook_data.product_id,
            current_stock=webhook_data.current_stock,
        )

        return AlertResponse(
            success=True,
            message="Alerta procesada y registrada exitosamente",
            alert_text=alert_message,
            supplier_price=supplier_price,
        )

    except Exception as e:
        logger.error(
            "webhook_processing_error",
            product_id=webhook_data.product_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando alerta: {str(e)}",
        )
