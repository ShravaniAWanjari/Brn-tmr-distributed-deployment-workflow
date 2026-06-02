# Brain Tumor MRI Classification - ML Pipeline

This directory contains the machine learning pipeline responsible for model training, validation, and ONNX export for the Brain Tumor classification project.

## Architecture Choice

**Model**: `EfficientNet-B0` (Pre-trained on ImageNet).

**Why?**
EfficientNet was chosen because it achieves state-of-the-art accuracy while being highly parameter-efficient. Medical image datasets (like MRI scans) often suffer from limited sample sizes, making training a deep architecture from scratch prone to overfitting. By using Transfer Learning with a pre-trained EfficientNet, we leverage its robust feature extraction capabilities and only fine-tune the classification head for our specific 4-class problem (Glioma, Meningioma, Pituitary, No Tumor).

## Training Workflow

**Script**: `ml/training/train.py`

1. **Reproducibility**: The script uses a `set_seed()` function guaranteeing that PyTorch, NumPy, and Python's random generators are fixed. This ensures deterministic behavior across distributed training nodes.
2. **Optimization**: We use the AdamW optimizer alongside a `ReduceLROnPlateau` Learning Rate Scheduler, which automatically decreases the learning rate if validation loss stops improving.
3. **Early Stopping & Checkpointing**: The custom callback in `ml/training/callbacks.py` constantly monitors the validation loss. If the loss fails to improve for 7 epochs, training is halted early to prevent overfitting, and the absolute best performing model state is saved to `ml/artifacts/best_model.pth`.

## Validation Workflow

**Script**: `ml/evaluation/evaluate.py`

After training, the best model is loaded to process the unseen test dataset. The evaluation script focuses on generating formal comparison metrics out of the raw logits:
- **Metrics**: Uses `scikit-learn` to calculate Accuracy, Precision, Recall, F1-score, and ROC AUC, outputting them into `ml/artifacts/metrics.json`.
- **Classification Report**: A detailed breakdown of performance per class is saved to `ml/artifacts/classification_report.json`.
- **Visuals**: A Seaborn-generated confusion matrix is saved to `ml/artifacts/confusion_matrix.png` to help visualize true vs. predicted misclassifications.

## Model Export Workflow

**Script**: `ml/models/export_onnx.py`

Once validated, the PyTorch weights (`best_model.pth`) are loaded back into a clean `EfficientNet-B0` graph. The script then feeds a dummy tensor `(1, 3, 224, 224)` through the network and utilizes `torch.onnx.export` to trace the computation graph.

The output is `ml/artifacts/best_model.onnx`. This ONNX format completely decouples the model from Python/PyTorch dependencies, enabling high-performance inference via ONNX Runtime in production backends.
