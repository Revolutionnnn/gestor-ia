from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    keywords = Column(JSONB, nullable=False, default=[])
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text)
    category = Column(String(300))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_stock_non_negative'),
    )
