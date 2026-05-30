import os
import yaml
import pytest
import torch
from data.loaders.dataloader import get_dataloaders

@pytest.fixture
def config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'data_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_dataloader_shapes(config):
    """
    Test if the DataLoader returns tensors of the correct shape and type.
    """
    train_loader, test_loader = get_dataloaders(config)
    
    # Check train loader
    images, labels = next(iter(train_loader))
    
    batch_size = config['dataloader']['batch_size']
    target_size = config['transforms']['target_size']
    
    assert images.shape == (batch_size, 3, target_size[0], target_size[1]), f"Unexpected image shape: {images.shape}"
    assert labels.shape == (batch_size,), f"Unexpected labels shape: {labels.shape}"
    assert isinstance(images, torch.Tensor), "Images should be torch tensors"
    assert isinstance(labels, torch.Tensor), "Labels should be torch tensors"
