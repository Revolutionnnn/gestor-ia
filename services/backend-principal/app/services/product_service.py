import asyncio
from typing import List

import httpx
from sqlalchemy.orm import Session

from ..config import (ALERTS_SERVICE_URL, ALERTS_WEBHOOK_TIMEOUT,
                      LOW_STOCK_THRESHOLD, logger)
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

    async def sell_product(self, product: Product) -> Product:
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

        # Verificar y enviar alerta de stock bajo en segundo plano
        if self.needs_stock_alert(product):
            asyncio.create_task(self._send_stock_alert(product))

        return product

    def needs_stock_alert(self, product: Product) -> bool:
        return product.stock < LOW_STOCK_THRESHOLD

    async def _send_stock_alert(self, product: Product) -> None:
        """
        Envía una alerta al microservicio de alertas cuando el stock es bajo.
        
        Args:
            product: Producto con stock bajo
        """
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
            # Log del error pero no falla la venta
            logger.error(
                "stock_alert_error",
                product_id=str(product.id),
                error=str(e),
            )
