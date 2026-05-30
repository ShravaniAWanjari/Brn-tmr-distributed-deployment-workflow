import os
import pytest
from data.loaders.dataset import BrainTumorDataset
from unittest.mock import patch
from PIL import UnidentifiedImageError

def test_corrupted_image_handling():
    """
    Test if the dataset gracefully handles or properly raises an exception 
    when an image is corrupted (simulated via mocking).
    """
    dummy_classes = ['glioma']
    
    # We create a minimal mock dataset
    dataset = BrainTumorDataset.__new__(BrainTumorDataset)
    dataset.classes = dummy_classes
    dataset.class_to_idx = {'glioma': 0}
    dataset.image_paths = ['fake_corrupted_image.jpg']
    dataset.labels = [0]
    dataset.transform = None

    with patch('data.loaders.dataset.Image.open') as mock_open:
        mock_open.side_effect = UnidentifiedImageError("Simulated corruption")
        
        with pytest.raises(ValueError, match="Corrupted or invalid image file"):
            _ = dataset[0]
