from pydantic import BaseModel, Field
from typing import Dict, List

class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="The predicted class name")
    confidence: float = Field(..., description="Confidence score of the prediction (0.0 to 1.0)")
    probabilities: Dict[str, float] = Field(..., description="Probabilities for all classes")
    inference_time_ms: float = Field(..., description="Time taken for model inference in milliseconds")

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse] = Field(..., description="List of predictions for the batch")
    total_inference_time_ms: float = Field(..., description="Total inference time for the entire batch")
