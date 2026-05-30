from torch.utils.data import DataLoader
from .dataset import BrainTumorDataset
from ..transforms.augmentations import get_train_transforms, get_test_transforms

def get_dataloaders(config):
    """
    Creates and returns the train and test DataLoaders.
    """
    root_dir = config['dataset']['root_dir']
    train_split = config['dataset']['train_split']
    test_split = config['dataset']['test_split']
    classes = config['dataset']['classes']
    
    batch_size = config['dataloader']['batch_size']
    num_workers = config['dataloader']['num_workers']
    shuffle_train = config['dataloader']['shuffle_train']
    drop_last_train = config['dataloader']['drop_last_train']

    train_transform = get_train_transforms(config)
    test_transform = get_test_transforms(config)

    train_dataset = BrainTumorDataset(
        root_dir=root_dir,
        split=train_split,
        classes=classes,
        transform=train_transform
    )

    test_dataset = BrainTumorDataset(
        root_dir=root_dir,
        split=test_split,
        classes=classes,
        transform=test_transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        num_workers=num_workers,
        drop_last=drop_last_train
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        drop_last=False
    )

    return train_loader, test_loader
