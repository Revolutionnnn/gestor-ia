from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import ProductCreate, ProductResponse, SellResponse
from ..services.product_service import ProductService
from ..services.alert_service import send_low_stock_alert
from ..dependencies import get_product_or_404
from ..config import logger

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    try:
        service = ProductService(db)
        return await service.create_product(product)
    except Exception as e:
        logger.error("create_product_error", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("", response_model=List[ProductResponse])
async def list_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.list_products()


@router.post("/{product_id}/sell", response_model=SellResponse)
async def sell_product(
    product_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    product = get_product_or_404(product_id, db)

    service = ProductService(db)
    product = service.sell_product(product)

    alert_will_be_sent = service.needs_stock_alert(product)

    if alert_will_be_sent:
        background_tasks.add_task(
            send_low_stock_alert,
            str(product.id),
            product.name,
            product.stock,
        )
        logger.info(
            "low_stock_alert_scheduled",
            product_id=str(product.id),
            stock=product.stock
        )
    
    return SellResponse(
        id=product.id,
        name=product.name,
        stock=product.stock,
        low_stock_alert_sent=alert_will_be_sent,
    )
