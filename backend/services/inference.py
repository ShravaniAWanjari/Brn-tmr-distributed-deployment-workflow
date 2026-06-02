import time
import numpy as np
import onnxruntime as ort
from PIL import Image
import io
import structlog
from typing import Tuple, List, Dict
from utils.config import settings
from metrics.prometheus import INFERENCE_LATENCY, PREDICTION_COUNT

logger = structlog.get_logger()

class ModelService:
    def __init__(self):
        self.session = None
        self.input_name = None
        self.classes = settings.CLASSES
        self.model_version = "v1"

    def load_model(self):
        """Loads the ONNX model into an InferenceSession."""
        try:
            # For a production deployment, consider setting execution providers explicitly (e.g., CUDAExecutionProvider)
            self.session = ort.InferenceSession(settings.MODEL_PATH, providers=["CPUExecutionProvider"])
            self.input_name = self.session.get_inputs()[0].name
            logger.info("Model loaded successfully", model_path=settings.MODEL_PATH)
        except Exception as e:
            logger.error("Failed to load model", error=str(e), model_path=settings.MODEL_PATH)
            raise e

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Resizes, normalizes and expands image to shape (1, 3, 224, 224)."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = image.resize((224, 224))
        
        # Convert to numpy array and scale to [0, 1]
        img_arr = np.array(image, dtype=np.float32) / 255.0
        
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_arr = (img_arr - mean) / std
        
        # HWC to CHW
        img_arr = np.transpose(img_arr, (2, 0, 1))
        
        # Add batch dimension
        img_arr = np.expand_dims(img_arr, axis=0)
        return img_arr

    def postprocess(self, logits: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """Applies softmax and maps to class labels."""
        # Calculate softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum(axis=1, keepdims=True)
        probs = probs[0] # batch size is 1 here
        
        predicted_idx = np.argmax(probs)
        predicted_class = self.classes[predicted_idx]
        confidence = float(probs[predicted_idx])
        
        probabilities = {cls: float(prob) for cls, prob in zip(self.classes, probs)}
        
        return predicted_class, confidence, probabilities

    def predict_single(self, image_bytes: bytes) -> dict:
        """Executes full inference pipeline for a single image."""
        start_time = time.perf_counter()
        
        input_tensor = self.preprocess(image_bytes)
        
        # Run inference
        inf_start = time.perf_counter()
        outputs = self.session.run(None, {self.input_name: input_tensor})
        inf_time = time.perf_counter() - inf_start
        
        # Record Prometheus metric
        INFERENCE_LATENCY.labels(model_version=self.model_version).observe(inf_time)
        
        logits = outputs[0]
        predicted_class, confidence, probabilities = self.postprocess(logits)
        
        # Record class prediction metric
        PREDICTION_COUNT.labels(predicted_class=predicted_class).inc()
        
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        logger.info("Prediction generated", predicted_class=predicted_class, confidence=confidence, inference_time_ms=total_time_ms)
        
        return {
            "prediction": predicted_class,
            "confidence": confidence,
            "probabilities": probabilities,
            "inference_time_ms": total_time_ms
        }
        
    def predict_batch(self, batch_bytes: List[bytes]) -> Tuple[List[dict], float]:
        """Executes inference on a batch of images sequentially (or can be vectorized)."""
        start_time = time.perf_counter()
        results = []
        for img_bytes in batch_bytes:
            results.append(self.predict_single(img_bytes))
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return results, total_time_ms

model_service = ModelService()
