import torchvision.transforms as T

def get_train_transforms(config):
    """
    Returns composed torchvision transforms for the training set.
    Includes data augmentation and normalization.
    """
    size = tuple(config['transforms']['target_size'])
    mean = config['transforms']['mean']
    std = config['transforms']['std']
    rot_deg = config['transforms']['rotation_degrees']
    bright = config['transforms']['brightness_jitter']
    contrast = config['transforms']['contrast_jitter']

    return T.Compose([
        T.Resize(size),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomRotation(degrees=rot_deg),
        T.ColorJitter(brightness=bright, contrast=contrast),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std)
    ])

def get_test_transforms(config):
    """
    Returns composed torchvision transforms for validation/test sets.
    Includes only resizing and normalization.
    """
    size = tuple(config['transforms']['target_size'])
    mean = config['transforms']['mean']
    std = config['transforms']['std']

    return T.Compose([
        T.Resize(size),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std)
    ])
