import os
from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset
import logging

class BrainTumorDataset(Dataset):
    def __init__(self, root_dir, split, classes, transform=None):
        """
        Custom Dataset for Brain Tumor MRI images.
        """
        self.root_dir = root_dir
        self.split = split
        self.classes = classes
        self.transform = transform
        
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        self.image_paths = []
        self.labels = []
        
        self._load_dataset()

    def _load_dataset(self):
        split_dir = os.path.join(self.root_dir, self.split)
        if not os.path.exists(split_dir):
            raise FileNotFoundError(f"Directory not found: {split_dir}")

        for cls_name in self.classes:
            cls_dir = os.path.join(split_dir, cls_name)
            if not os.path.exists(cls_dir):
                logging.warning(f"Class directory not found: {cls_dir}")
                continue
                
            for fname in os.listdir(cls_dir):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.image_paths.append(os.path.join(cls_dir, fname))
                    self.labels.append(self.class_to_idx[cls_name])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            # Load image and convert to RGB
            image = Image.open(img_path).convert('RGB')
        except (UnidentifiedImageError, OSError) as e:
            # Handle corrupted images by raising an exception or returning a specific flag
            # For production readiness, logging and raising allows the pipeline to catch bad data
            raise ValueError(f"Corrupted or invalid image file: {img_path}") from e

        if self.transform:
            image = self.transform(image)

        return image, label
