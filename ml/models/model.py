import torch
import torch.nn as nn
import torchvision.models as models

def get_efficientnet_b0(num_classes=4, pretrained=True, freeze_base=False):
    """
    Returns an EfficientNet-B0 model with a custom classification head.
    """
    # Load pretrained EfficientNet-B0
    if pretrained:
        weights = models.EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=weights)
    else:
        model = models.efficientnet_b0(weights=None)
        
    if freeze_base:
        for param in model.parameters():
            param.requires_grad = False
            
    # Replace the classifier head
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    
    return model
