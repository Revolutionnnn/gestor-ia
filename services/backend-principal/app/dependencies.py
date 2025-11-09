from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from .database import get_db
from .models import Product


def get_product_or_404(product_id: str, db: Session = Depends(get_db)) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product
