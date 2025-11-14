import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    keywords: List[str] = Field(..., min_items=1, max_items=10)
    stock: int = Field(..., ge=0)
    price: int = Field(..., ge=0)
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

    @validator("keywords")
    def clean_keywords(cls, v):
        return [k.strip() for k in v if k.strip()]


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    keywords: Optional[List[str]] = Field(None, min_items=1, max_items=10)
    stock: Optional[int] = Field(None, ge=0)
    price: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

    @validator("keywords")
    def clean_keywords(cls, v):
        if v is not None:
            return [k.strip() for k in v if k.strip()]
        return v


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    keywords: List[str]
    stock: int
    price: int
    description: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    is_active: bool
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
