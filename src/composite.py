import json
import os
from PIL import Image


def hard_paste(original_path, edited_patch_path, meta_path, out_path):
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    bx1, by1, bx2, by2 = meta['buffered_bbox']

    original = Image.open(original_path).convert("RGBA")
    edited_patch = Image.open(edited_patch_path).convert("RGBA")

    patch_width = bx2 - bx1
    patch_height = by2 - by1
    if edited_patch.size != (patch_width, patch_height):
        edited_patch = edited_patch.resize((patch_width, patch_height), Image.Resampling.LANCZOS)

    result = original.copy()
    result.paste(edited_patch, (bx1, by1))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result.save(out_path, 'PNG')
    return out_path
