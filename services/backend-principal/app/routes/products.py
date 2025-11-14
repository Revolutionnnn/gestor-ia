from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config import logger
from ..database import get_db
from ..dependencies import get_admin_user, get_current_user
from ..schemas import (ProductCreate, ProductResponse, ProductUpdate,
                       SellResponse)
from ..services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


# ==============================================================================
# ENDPOINTS PÚBLICOS - No requieren autenticación
# ==============================================================================

@router.get(
    "",
    response_model=List[ProductResponse],
    summary="Listar productos activos (público)",
)
async def list_products_public(db: Session = Depends(get_db)):
    """
    Lista todos los productos activos y disponibles para el público.
    
    **Endpoint público - no requiere autenticación.**
    
    Solo muestra productos con `is_active=True`.
    """
    service = ProductService(db)
    return service.list_products_public()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Ver detalle de producto (público)",
)
async def get_product_public(product_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un producto activo.
    
    **Endpoint público - no requiere autenticación.**
    
    Solo muestra el producto si está activo (`is_active=True`).
    """
    service = ProductService(db)
    return service.get_product_public(product_id)


# ==============================================================================
# ENDPOINTS DE USUARIO AUTENTICADO
# ==============================================================================

@router.post(
    "/{product_id}/sell",
    response_model=SellResponse,
    summary="Vender producto (requiere autenticación)",
)
async def sell_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Registra la venta de una unidad del producto.
    
    **Requiere autenticación (cualquier usuario autenticado).**
    
    - Reduce el stock en 1
    - Envía alerta si el stock es bajo
    - Solo funciona con productos activos
    """
    service = ProductService(db)
    product = service.get_product_public(product_id)
    
    product = await service.sell_product(product)
    
    logger.info(
        "product_sold",
        product_id=str(product.id),
        sold_by=user.get("username"),
        remaining_stock=product.stock,
    )

    return SellResponse(
        id=product.id,
        name=product.name,
        stock=product.stock,
    )


# ==============================================================================
# ENDPOINTS DE ADMINISTRADOR - Requieren rol admin
# ==============================================================================

@router.get(
    "/admin/all",
    response_model=List[ProductResponse],
    summary="Listar todos los productos (admin)",
)
async def list_all_products_admin(
    db: Session = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    """
    Lista todos los productos (activos e inactivos).
    
    **Requiere autenticación con rol de administrador.**
    
    Muestra productos con cualquier estado de `is_active`.
    """
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
    """
    Obtiene el detalle de cualquier producto (activo o inactivo).
    
    **Requiere autenticación con rol de administrador.**
    """
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
    """
    Crea un nuevo producto en el catálogo.
    
    **Requiere autenticación con rol de administrador.**
    
    Si no se proporciona descripción o categoría, se generan con IA.
    """
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
    """
    Actualiza un producto existente.
    
    **Requiere autenticación con rol de administrador.**
    
    - Permite actualización parcial (solo campos proporcionados)
    - Si se actualiza nombre/keywords, regenera descripción con IA
    - Si se actualiza descripción, regenera categoría con IA
    - Se puede activar/desactivar con `is_active`
    """
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
    """
    Elimina permanentemente un producto.
    
    **Requiere autenticación con rol de administrador.**
    
    **Advertencia**: Esta acción no se puede deshacer.
    
    Para ocultar temporalmente un producto, considera usar
    `PUT /{product_id}` con `is_active=false` en su lugar.
    """
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
