import uuid

from sqlalchemy import (JSON, TIMESTAMP, Boolean, CheckConstraint, Column,
                        Integer, String, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    keywords = Column(JSON, nullable=False, default=[])
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Integer, nullable=False, default=0)
    description = Column(Text)
    category = Column(String(300))
    image_url = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
    )
