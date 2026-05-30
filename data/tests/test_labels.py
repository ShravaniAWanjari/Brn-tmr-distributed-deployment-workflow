import os
import yaml
import pytest
from data.loaders.dataset import BrainTumorDataset

@pytest.fixture
def config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'data_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_label_consistency(config):
    """
    Test if the dataset class consistently maps classes to the same integers.
    """
    root_dir = config['dataset']['root_dir']
    classes = config['dataset']['classes']
    train_split = config['dataset']['train_split']
    
    dataset = BrainTumorDataset(
        root_dir=root_dir,
        split=train_split,
        classes=classes
    )
    
    expected_mapping = {cls_name: i for i, cls_name in enumerate(classes)}
    assert dataset.class_to_idx == expected_mapping, f"Label mapping mismatch. Expected {expected_mapping}, got {dataset.class_to_idx}"
    
    # Check that labels generated are within valid range
    for label in set(dataset.labels):
        assert 0 <= label < len(classes), f"Label {label} is out of bounds for {len(classes)} classes."
