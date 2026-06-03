import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from services.inference import ModelService
from utils.config import settings

@pytest.fixture
def model_service():
    service = ModelService()
    # Mock the ONNX InferenceSession
    service.session = MagicMock()
    service.input_name = "input"
    return service

def test_postprocess(model_service):
    # Simulate logits output from the model
    # Suppose index 0 ('glioma') is the highest
    logits = np.array([[5.0, 1.0, 0.5, 0.1]])
    
    predicted_class, confidence, probabilities = model_service.postprocess(logits)
    
    assert predicted_class == settings.CLASSES[0]
    assert confidence > 0.9  # Should be very high given logits
    assert isinstance(probabilities, dict)
    assert len(probabilities) == 4
    
@patch("services.inference.Image.open")
def test_preprocess(mock_open, model_service):
    # Create a dummy image
    from PIL import Image
    dummy_img = Image.new('RGB', (300, 300), color='red')
    mock_open.return_value = dummy_img
    
    # Pass dummy bytes
    tensor = model_service.preprocess(b"dummy_bytes")
    
    # Expected shape for ONNX input: (1, 3, 224, 224)
    assert tensor.shape == (1, 3, 224, 224)
    assert tensor.dtype == np.float32
