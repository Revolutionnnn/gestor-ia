from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config import logger
from ..database import get_db
from ..dependencies import get_product_or_404
from ..schemas import ProductCreate, ProductResponse, SellResponse
from ..services.product_service import ProductService

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
    db: Session = Depends(get_db),
):
    product = get_product_or_404(product_id, db)

    service = ProductService(db)
    product = await service.sell_product(product)

    return SellResponse(
        id=product.id,
        name=product.name,
        stock=product.stock,
    )
