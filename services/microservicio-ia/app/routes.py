from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import time

from models import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    GenerateCategoryRequest,
    GenerateCategoryResponse,
    HealthResponse
)
from llm_service import llm_service
from prompts import (
    build_description_prompt,
    build_category_prompt,
    DESCRIPTION_SYSTEM_MESSAGE
)
from config import logger, OPENAI_MODEL

router = APIRouter()


@router.get("/")
async def root():
    return {
        "service": "Microservicio IA",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "generate_description": "POST /generate/description",
            "generate_category": "POST /generate/category"
        }
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if llm_service.is_configured() else "degraded",
        service="microservicio-ia",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        llm_configured=llm_service.is_configured(),
        model=OPENAI_MODEL if llm_service.is_configured() else "not_configured"
    )


@router.post("/generate/description", response_model=GenerateDescriptionResponse)
async def generate_description(request: GenerateDescriptionRequest):
    start_time = time.time()
    
    logger.info(
        "generate_description_request",
        product_name=request.name,
        keywords_count=len(request.keywords)
    )
    
    try:
        prompt = build_description_prompt(request.name, request.keywords)
        description, tokens = llm_service.generate(prompt, DESCRIPTION_SYSTEM_MESSAGE)
        
        processing_time = time.time() - start_time
        
        logger.info(
            "generate_description_success",
            product_name=request.name,
            processing_time=processing_time,
            tokens_used=tokens
        )
        
        return GenerateDescriptionResponse(
            generated_description=description.strip(),
            processing_time=round(processing_time, 2),
            model_used=OPENAI_MODEL,
            tokens_used=tokens
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("generate_description_error", error=str(e), product_name=request.name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando descripción: {str(e)}"
        )


@router.post("/generate/category", response_model=GenerateCategoryResponse)
async def generate_category(request: GenerateCategoryRequest):
    start_time = time.time()
    
    logger.info("generate_category_request", product_name=request.product_name)
    
    try:
        prompt = build_category_prompt(request.product_name, request.description)
        category, tokens = llm_service.generate(prompt)
        
        processing_time = time.time() - start_time
        category = category.strip()
        
        parts = [p.strip() for p in category.split(">")]
        confidence = min(1.0, len(parts) / 3.0)
        
        logger.info(
            "generate_category_success",
            product_name=request.product_name,
            category=category,
            confidence=confidence,
            processing_time=processing_time
        )
        
        return GenerateCategoryResponse(
            suggested_category=category,
            confidence=round(confidence, 2),
            processing_time=round(processing_time, 2),
            model_used=OPENAI_MODEL
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("generate_category_error", error=str(e), product_name=request.product_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando categoría: {str(e)}"
        )
