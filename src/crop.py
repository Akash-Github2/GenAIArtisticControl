import json
import os
from pathlib import Path
from PIL import Image


def get_image_name(image_path):
    return Path(image_path).stem


def get_patch_subdirectory(image_path, base_dir="data/patches"):
    image_name = get_image_name(image_path)
    subdir = os.path.join(base_dir, image_name)
    os.makedirs(subdir, exist_ok=True)
    return subdir


def crop_region(image_path, x1, y1, x2, y2, out_path):
    img = Image.open(image_path).convert("RGBA")
    patch = img.crop((x1, y1, x2, y2))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    patch.save(out_path, 'PNG')

    return (x1, y1, x2, y2)


def save_crop_metadata(meta_dict, meta_path):
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, 'w') as f:
        json.dump(meta_dict, f, indent=2)


def load_crop_metadata(meta_path):
    with open(meta_path, 'r') as f:
        return json.load(f)
