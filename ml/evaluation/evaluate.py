import os
import yaml
import json
import logging
import torch
import torch.nn.functional as F
import sys

# Ensure data and ml packages are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from data.loaders.dataloader import get_dataloaders
from ml.models.model import get_efficientnet_b0
from ml.evaluation.metrics import calculate_metrics

def evaluate_model(train_config_path, data_config_path):
    with open(train_config_path, 'r') as f:
        config = yaml.safe_load(f)
    with open(data_config_path, 'r') as f:
        data_config = yaml.safe_load(f)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Dataloader (use test_loader for evaluation)
    _, test_loader = get_dataloaders(data_config)

    # Load Model
    model = get_efficientnet_b0(num_classes=config['model']['num_classes'], pretrained=False)
    ckpt_path = os.path.join(config['paths']['checkpoint_dir'], config['paths']['best_model_name'])
    
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"No checkpoint found at {ckpt_path}. Run training first.")
        
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model = model.to(device)
    model.eval()

    all_labels = []
    all_preds = []
    all_probs = []

    logging.info("Starting evaluation...")
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            
            probs = F.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    # Calculate metrics
    metrics = calculate_metrics(all_labels, all_preds, all_probs)
    
    # Save Report
    os.makedirs(config['paths']['report_dir'], exist_ok=True)
    report_path = os.path.join(config['paths']['report_dir'], 'performance_report.json')
    
    with open(report_path, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    logging.info(f"Evaluation complete. Metrics saved to {report_path}")
    logging.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logging.info(f"F1 Score: {metrics['f1']:.4f}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_cfg = os.path.join(os.path.dirname(__file__), '..', 'configs', 'train_config.yaml')
    data_cfg = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'configs', 'data_config.yaml')
    evaluate_model(train_cfg, data_cfg)
