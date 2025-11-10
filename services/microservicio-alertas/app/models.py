from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StockAlertWebhook(BaseModel):
    product_id: str = Field(..., description="ID del producto")
    product_name: str = Field(..., description="Nombre del producto")
    current_stock: int = Field(..., ge=0, description="Stock actual del producto")


class AlertResponse(BaseModel):
    success: bool
    message: str
    alert_text: Optional[str] = None
    supplier_price: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
