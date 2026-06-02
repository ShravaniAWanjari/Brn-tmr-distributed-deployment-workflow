import os
import yaml
import logging
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import sys
import random
import numpy as np

def set_seed(seed=42):
    """Sets the seed for reproducible training."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Ensure data package is importable from the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from data.loaders.dataloader import get_dataloaders
from ml.models.model import get_efficientnet_b0
from ml.training.callbacks import EarlyStopping

def train_model(train_config_path, data_config_path):
    set_seed(42)
    
    with open(train_config_path, 'r') as f:
        config = yaml.safe_load(f)
    with open(data_config_path, 'r') as f:
        data_config = yaml.safe_load(f)

    # Setup directories
    os.makedirs(config['paths']['artifacts_dir'], exist_ok=True)
    os.makedirs(config['paths']['tensorboard_dir'], exist_ok=True)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Using device: {device}")

    # Data Loaders
    train_loader, val_loader = get_dataloaders(data_config)

    # Model
    model = get_efficientnet_b0(
        num_classes=config['model']['num_classes'],
        pretrained=config['model']['pretrained'],
        freeze_base=config['model']['freeze_base']
    )
    model = model.to(device)

    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), 
                            lr=config['training']['learning_rate'], 
                            weight_decay=config['training']['weight_decay'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=3)

    # Callbacks & Logging
    ckpt_path = os.path.join(config['paths']['artifacts_dir'], config['paths']['best_model_name'])
    early_stopping = EarlyStopping(patience=config['training']['patience'], verbose=True, path=ckpt_path)
    writer = SummaryWriter(log_dir=config['paths']['tensorboard_dir'])

    num_epochs = config['training']['epochs']
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        epoch_train_loss = train_loss / len(train_loader.dataset)
        epoch_train_acc = correct / total

        # Validation phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
        epoch_val_loss = val_loss / len(val_loader.dataset)
        epoch_val_acc = correct / total

        logging.info(f"Epoch [{epoch+1}/{num_epochs}] - "
                     f"Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.4f} - "
                     f"Val Loss: {epoch_val_loss:.4f}, Val Acc: {epoch_val_acc:.4f}")

        # TensorBoard logging
        writer.add_scalar('Loss/train', epoch_train_loss, epoch)
        writer.add_scalar('Loss/val', epoch_val_loss, epoch)
        writer.add_scalar('Accuracy/train', epoch_train_acc, epoch)
        writer.add_scalar('Accuracy/val', epoch_val_acc, epoch)
        writer.add_scalar('LR', optimizer.param_groups[0]['lr'], epoch)

        # LR Scheduling and Early Stopping
        scheduler.step(epoch_val_loss)
        early_stopping(epoch_val_loss, model)
        
        if early_stopping.early_stop:
            logging.info("Early stopping triggered")
            break

    writer.close()
    logging.info("Training complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_cfg = os.path.join(os.path.dirname(__file__), '..', 'configs', 'train_config.yaml')
    data_cfg = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'configs', 'data_config.yaml')
    train_model(train_cfg, data_cfg)
