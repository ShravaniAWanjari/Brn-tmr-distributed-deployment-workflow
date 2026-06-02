import os
import torch
import logging
import sys

# Ensure ml package is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ml.models.model import get_efficientnet_b0

def export_to_onnx(config):
    """
    Loads the best PyTorch checkpoint and exports it to ONNX format.
    """
    ckpt_dir = config['paths']['artifacts_dir']
    pth_path = os.path.join(ckpt_dir, config['paths']['best_model_name'])
    onnx_path = os.path.join(ckpt_dir, config['paths']['onnx_export_name'])
    
    if not os.path.exists(pth_path):
        raise FileNotFoundError(f"Checkpoint not found at {pth_path}")
        
    num_classes = config['model']['num_classes']
    model = get_efficientnet_b0(num_classes=num_classes, pretrained=False)
    
    # Load weights
    model.load_state_dict(torch.load(pth_path, map_location='cpu'))
    model.eval()
    
    # Create a dummy input corresponding to standard ImageNet input
    dummy_input = torch.randn(1, 3, 224, 224)
    
    # Export
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    logging.info(f"Model exported to ONNX format at: {onnx_path}")

if __name__ == "__main__":
    import yaml
    logging.basicConfig(level=logging.INFO)
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'train_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    export_to_onnx(config)
