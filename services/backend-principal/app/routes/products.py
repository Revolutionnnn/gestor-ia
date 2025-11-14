from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config import logger
from ..database import get_db
from ..services.auth_dependencies import get_admin_user, get_optional_user
from ..schemas import (ProductCreate, ProductResponse, ProductUpdate,
                       SellResponse)
from ..services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=List[ProductResponse],
    summary="Listar productos activos (público)",
)
async def list_products_public(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.list_products_public()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Ver detalle de producto (público)",
)
async def get_product_public(product_id: UUID, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product_public(product_id)


@router.post(
    "/{product_id}/sell",
    response_model=SellResponse,
    summary="Vender producto (público)",
)
async def sell_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: dict | None = Depends(get_optional_user),
):
    service = ProductService(db)
    product = service.get_product_public(product_id)

    product = await service.sell_product(product)

    logger.info(
        "product_sold",
        product_id=str(product.id),
        sold_by=user.get("username") if user else "guest",
        remaining_stock=product.stock,
    )

    return SellResponse(
        id=product.id,
        name=product.name,
        stock=product.stock,
    )


@router.get(
    "/admin/all",
    response_model=List[ProductResponse],
    summary="Listar todos los productos (admin)",
)
async def list_all_products_admin(
    db: Session = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    service = ProductService(db)
    return service.list_products_admin()


@router.get(
    "/admin/{product_id}",
    response_model=ProductResponse,
    summary="Ver cualquier producto (admin)",
)
async def get_product_admin(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    service = ProductService(db)
    return service.get_product_by_id(product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto (admin)",
)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    try:
        service = ProductService(db)
        result = await service.create_product(product)
        logger.info(
            "product_created",
            product_id=str(result.id),
            created_by=user.get("username"),
        )
        return result
    except Exception as e:
        logger.error("create_product_error", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Actualizar producto (admin)",
)
async def update_product(
    product_id: UUID,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    try:
        service = ProductService(db)
        result = await service.update_product(product_id, product)
        logger.info(
            "product_updated",
            product_id=str(result.id),
            updated_by=user.get("username"),
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_product_error", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto (admin)",
)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    try:
        service = ProductService(db)
        service.delete_product(product_id)
        logger.info(
            "product_deleted",
            product_id=str(product_id),
            deleted_by=user.get("username"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_product_error", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
