import os
import json
import logging
from collections import defaultdict

def generate_reports(config):
    """
    Generates dataset statistics and label mapping reports based on the configuration.
    Outputs JSON files to the configured reports directory.
    """
    root_dir = config['dataset']['root_dir']
    classes = config['dataset']['classes']
    splits = [config['dataset']['train_split'], config['dataset']['test_split']]
    
    reports_dir = config['reports']['output_dir']
    stats_file = config['reports']['stats_file']
    mapping_file = config['reports']['mapping_file']

    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    # 1. Generate label mapping
    label_mapping = {cls_name: i for i, cls_name in enumerate(classes)}
    mapping_path = os.path.join(reports_dir, mapping_file)
    with open(mapping_path, 'w') as f:
        json.dump(label_mapping, f, indent=4)
    logging.info(f"Saved label mapping to {mapping_path}")

    # 2. Generate dataset statistics
    stats = {
        "class_counts": {split: defaultdict(int) for split in splits},
        "total_images": 0
    }

    for split in splits:
        split_dir = os.path.join(root_dir, split)
        if not os.path.exists(split_dir):
            continue
        for cls_name in classes:
            cls_dir = os.path.join(split_dir, cls_name)
            if not os.path.exists(cls_dir):
                continue
            count = len([f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            stats["class_counts"][split][cls_name] = count
            stats["total_images"] += count

    # Convert defaultdicts to regular dicts for JSON serialization
    stats["class_counts"] = {k: dict(v) for k, v in stats["class_counts"].items()}
    
    stats_path = os.path.join(reports_dir, stats_file)
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=4)
    logging.info(f"Saved dataset statistics to {stats_path}")

if __name__ == "__main__":
    import yaml
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'data_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logging.basicConfig(level=logging.INFO)
    generate_reports(config)
