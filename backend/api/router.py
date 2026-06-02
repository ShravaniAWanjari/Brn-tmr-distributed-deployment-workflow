from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import structlog

from schemas.payload import PredictionResponse, BatchPredictionResponse
from api.dependencies import get_model_service

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "brain_tumor_classification"}

@router.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict(file: UploadFile = File(...), model_service = Depends(get_model_service)):
    """Single image prediction endpoint."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        image_bytes = await file.read()
        result = model_service.predict_single(image_bytes)
        return result
    except Exception as e:
        logger.exception("Error during prediction", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during inference.")

@router.post("/batch-predict", response_model=BatchPredictionResponse, tags=["Inference"])
async def batch_predict(files: List[UploadFile] = File(...), model_service = Depends(get_model_service)):
    """Batch image prediction endpoint."""
    image_bytes_list = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image.")
        image_bytes_list.append(await file.read())
        
    try:
        results, total_time = model_service.predict_batch(image_bytes_list)
        return {"results": results, "total_inference_time_ms": total_time}
    except Exception as e:
        logger.exception("Error during batch prediction", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during batch inference.")
