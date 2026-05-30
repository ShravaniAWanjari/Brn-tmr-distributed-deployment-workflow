import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

def calculate_metrics(y_true, y_pred, y_prob):
    """
    Calculate comprehensive classification metrics.
    """
    metrics = {}
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    
    # Calculate macro-averaged precision, recall, and f1
    metrics['precision'] = precision_score(y_true, y_pred, average='macro', zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, average='macro', zero_division=0)
    metrics['f1'] = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    # Calculate ROC AUC if probabilities are provided and multi-class is properly handled
    try:
        metrics['roc_auc'] = roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro')
    except Exception:
        metrics['roc_auc'] = None

    metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()
    
    return metrics
