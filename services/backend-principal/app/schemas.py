import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    keywords: List[str] = Field(..., min_items=1, max_items=10)
    stock: int = Field(..., ge=0)

    @validator("keywords")
    def clean_keywords(cls, v):
        return [k.strip() for k in v if k.strip()]


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    keywords: List[str]
    stock: int
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SellResponse(BaseModel):
    id: uuid.UUID
    name: str
    stock: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    dependencies: dict
