from typing import List

from sqlalchemy.orm import Session

from ..config import logger
from ..models import Product
from ..schemas import ProductCreate
from .ia_client import generate_category, generate_description


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def create_product(self, product_data: ProductCreate) -> Product:
        logger.info("create_product_request", name=product_data.name)

        description = await generate_description(
            product_data.name,
            product_data.keywords,
        )
        category = await generate_category(product_data.name, description)

        db_product = Product(
            name=product_data.name,
            keywords=product_data.keywords,
            stock=product_data.stock,
            description=description,
            category=category,
        )

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        logger.info(
            "product_created",
            product_id=str(db_product.id),
            name=product_data.name,
        )

        return db_product

    def list_products(self) -> List[Product]:
        return self.db.query(Product).all()

    def sell_product(self, product: Product) -> Product:
        if product.stock <= 0:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuficiente",
            )

        product.stock -= 1
        self.db.commit()
        self.db.refresh(product)

        logger.info(
            "product_sold",
            product_id=str(product.id),
            new_stock=product.stock,
        )

        return product

    def needs_stock_alert(self, product: Product) -> bool:
        from ..constants import LOW_STOCK_THRESHOLD

        return product.stock < LOW_STOCK_THRESHOLD
