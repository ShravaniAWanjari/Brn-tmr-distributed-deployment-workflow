import os
import yaml
import torch
import torch.nn.functional as F
from PIL import Image
import sys
import argparse

# Ensure data and ml packages are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ml.models.model import get_efficientnet_b0
from data.transforms.augmentations import get_test_transforms

def predict_image(image_path, train_config_path, data_config_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    with open(train_config_path, 'r') as f:
        config = yaml.safe_load(f)
    with open(data_config_path, 'r') as f:
        data_config = yaml.safe_load(f)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load Model
    model = get_efficientnet_b0(num_classes=config['model']['num_classes'], pretrained=False)
    ckpt_path = os.path.join(config['paths']['checkpoint_dir'], config['paths']['best_model_name'])
    
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"No checkpoint found at {ckpt_path}. Run training first.")
        
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model = model.to(device)
    model.eval()

    # Transformations
    transforms = get_test_transforms(data_config)
    classes = data_config['dataset']['classes']

    # Load and transform image
    image = Image.open(image_path).convert('RGB')
    tensor = transforms(image).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        outputs = model(tensor)
        probs = F.softmax(outputs, dim=1)
        conf, pred = torch.max(probs, 1)

    predicted_class = classes[pred.item()]
    confidence = conf.item()
    
    return predicted_class, confidence

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict brain tumor class for a single MRI image.")
    parser.add_argument('image_path', type=str, help="Path to the input image.")
    args = parser.parse_args()

    train_cfg = os.path.join(os.path.dirname(__file__), '..', 'configs', 'train_config.yaml')
    data_cfg = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'configs', 'data_config.yaml')
    
    pred_class, conf = predict_image(args.image_path, train_cfg, data_cfg)
    print(f"Prediction: {pred_class} (Confidence: {conf:.4f})")
