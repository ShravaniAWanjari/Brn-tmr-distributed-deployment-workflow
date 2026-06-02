import os
import yaml
import json
import logging
import torch
import torch.nn.functional as F
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

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
    ckpt_path = os.path.join(config['paths']['artifacts_dir'], config['paths']['best_model_name'])
    
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
    artifacts_dir = config['paths']['artifacts_dir']
    os.makedirs(artifacts_dir, exist_ok=True)
    
    metrics_path = os.path.join(artifacts_dir, config['paths']['metrics_name'])
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    # Generate and save classification report
    target_names = data_config['dataset']['classes']
    clf_report = classification_report(all_labels, all_preds, target_names=target_names, output_dict=True)
    clf_report_path = os.path.join(artifacts_dir, config['paths']['classification_report_name'])
    with open(clf_report_path, 'w') as f:
        json.dump(clf_report, f, indent=4)
        
    # Plot and save confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    cm_path = os.path.join(artifacts_dir, config['paths']['confusion_matrix_name'])
    plt.savefig(cm_path)
    plt.close()
        
    logging.info(f"Evaluation complete. Artifacts saved to {artifacts_dir}")
    logging.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logging.info(f"F1 Score: {metrics['f1']:.4f}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_cfg = os.path.join(os.path.dirname(__file__), '..', 'configs', 'train_config.yaml')
    data_cfg = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'configs', 'data_config.yaml')
    evaluate_model(train_cfg, data_cfg)
