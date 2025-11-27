"""
Health check endpoints for AI Service.
"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """Check service health and model status."""
    model_manager = getattr(request.app.state, 'model_manager', None)
    
    models_loaded = {}
    if model_manager:
        for name, model in model_manager.models.items():
            models_loaded[name] = {
                "loaded": True,
                "version": model.version,
                "accuracy": model.accuracy,
            }
    
    return {
        "status": "healthy",
        "service": "ai-service",
        "models": models_loaded,
    }


@router.get("/ready")
async def readiness_check(request: Request):
    """Check if service is ready to handle requests."""
    model_manager = getattr(request.app.state, 'model_manager', None)
    
    if not model_manager or not model_manager._initialized:
        return {"ready": False, "reason": "Models not loaded"}
    
    return {"ready": True, "models_count": len(model_manager.models)}
