import json
import os
from PIL import Image


def hard_paste(original_path, edited_patch_path, meta_path, out_path):
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    x1, y1, x2, y2 = meta['bbox']

    original = Image.open(original_path).convert("RGBA")
    edited_patch = Image.open(edited_patch_path).convert("RGBA")

    patch_width = x2 - x1
    patch_height = y2 - y1
    if edited_patch.size != (patch_width, patch_height):
        edited_patch = edited_patch.resize((patch_width, patch_height), Image.Resampling.LANCZOS)

    result = original.copy()
    result.paste(edited_patch, (x1, y1))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result.save(out_path, 'PNG')
    return out_path
