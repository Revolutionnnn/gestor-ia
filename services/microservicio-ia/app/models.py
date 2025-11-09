from typing import List

from pydantic import BaseModel, Field, validator


class GenerateDescriptionRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    keywords: List[str] = Field(..., min_items=1, max_items=10)
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if not v:
            raise ValueError('Debe proporcionar al menos una palabra clave')
        return [k.strip() for k in v if k.strip()]


class GenerateDescriptionResponse(BaseModel):
    generated_description: str
    processing_time: float
    model_used: str
    tokens_used: int


class GenerateCategoryRequest(BaseModel):
    product_name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)


class GenerateCategoryResponse(BaseModel):
    suggested_category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time: float
    model_used: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    llm_configured: bool
    model: str
