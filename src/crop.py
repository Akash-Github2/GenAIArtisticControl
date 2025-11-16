#!/usr/bin/env python3

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


def crop_with_buffer(image_path, x1, y1, x2, y2, padding, out_path):
    """Crop a patch with padding buffer for blending."""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # Add buffer, clamped to image bounds
    bx1 = max(0, x1 - padding)
    by1 = max(0, y1 - padding)
    bx2 = min(width, x2 + padding)
    by2 = min(height, y2 + padding)

    # Crop and save
    patch = img.crop((bx1, by1, bx2, by2))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    patch.save(out_path, 'PNG')

    return (bx1, by1, bx2, by2)


def save_crop_metadata(meta_dict, meta_path):
    """Save crop metadata to JSON."""
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, 'w') as f:
        json.dump(meta_dict, f, indent=2)


def load_crop_metadata(meta_path):
    """Load crop metadata from JSON."""
    with open(meta_path, 'r') as f:
        return json.load(f)
