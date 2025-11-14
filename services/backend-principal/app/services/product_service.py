import asyncio
from typing import Any, List
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import (ALERTS_SERVICE_URL, ALERTS_WEBHOOK_TIMEOUT,
                      LOW_STOCK_THRESHOLD, logger)
from ..infraestructure.ia_client import generate_category, generate_description
from ..models import Product
from ..schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def create_product(self, product_data: ProductCreate) -> Product:
        logger.info("create_product_request", name=product_data.name)

        description = product_data.description or await generate_description(
            product_data.name,
            product_data.keywords,
        )
        category = product_data.category or await generate_category(
            product_data.name,
            description,
        )

        db_product = Product(
            name=product_data.name,
            keywords=product_data.keywords,
            stock=product_data.stock,
            price=product_data.price,
            description=description,
            category=category,
            image_url=product_data.image_url,
            is_active=product_data.is_active,
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

    def list_products_public(self) -> List[Product]:
        return (
            self.db.query(Product)
            .filter(Product.is_active.is_(True))
            .all()
        )

    def list_products_admin(self) -> List[Product]:
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: UUID) -> Product:
        product = (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return product

    def get_product_public(self, product_id: UUID) -> Product:
        product = (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.is_active.is_(True))
            .first()
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado o no disponible",
            )
        return product

    async def update_product(
        self,
        product_id: UUID,
        product_data: ProductUpdate,
    ) -> Product:
        product = self.get_product_by_id(product_id)

        update_data: dict[str, Any] = product_data.model_dump(
            exclude_unset=True,
        )

        if self._should_refresh_description(update_data):
            new_name = update_data.get("name", product.name)
            new_keywords = update_data.get("keywords", product.keywords)
            update_data["description"] = await generate_description(
                new_name,
                new_keywords,
            )

        if "description" in update_data:
            new_name = update_data.get("name", product.name)
            update_data["category"] = await generate_category(
                new_name,
                update_data["description"],
            )

        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)

        logger.info(
            "product_updated",
            product_id=str(product.id),
            updated_fields=list(update_data.keys()),
        )

        return product

    def delete_product(self, product_id: UUID) -> None:
        product = self.get_product_by_id(product_id)

        self.db.delete(product)
        self.db.commit()

        logger.info(
            "product_deleted",
            product_id=str(product.id),
            name=product.name,
        )

    async def sell_product(self, product: Product) -> Product:
        if product.stock <= 0:
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

        if self.needs_stock_alert(product):
            asyncio.create_task(self._send_stock_alert(product))

        return product

    @staticmethod
    def _should_refresh_description(update_data: dict[str, Any]) -> bool:
        return (
            ("name" in update_data or "keywords" in update_data)
            and "description" not in update_data
        )

    def needs_stock_alert(self, product: Product) -> bool:
        return product.stock < LOW_STOCK_THRESHOLD

    async def _send_stock_alert(self, product: Product) -> None:
        """Send a low-stock webhook to the alerts microservice."""
        try:
            webhook_url = f"{ALERTS_SERVICE_URL}/webhook/stock-alert"
            payload = {
                "product_id": str(product.id),
                "product_name": product.name,
                "current_stock": product.stock,
            }

            logger.info(
                "sending_stock_alert",
                product_id=str(product.id),
                webhook_url=webhook_url,
            )

            async with httpx.AsyncClient(
                timeout=ALERTS_WEBHOOK_TIMEOUT
            ) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()

            logger.info(
                "stock_alert_sent",
                product_id=str(product.id),
                response_status=response.status_code,
            )

        except Exception as e:
            logger.error(
                "stock_alert_error",
                product_id=str(product.id),
                error=str(e),
            )
