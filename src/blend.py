import cv2
import json
import os
import numpy as np


def blend_patch_back(original_path, edited_patch_path, meta_path, out_path):
    # poisson blending via cv2.seamlessClone
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    x1, y1, x2, y2 = meta['bbox']

    original = cv2.imread(original_path)
    edited_patch = cv2.imread(edited_patch_path)

    patch_width = x2 - x1
    patch_height = y2 - y1
    if (edited_patch.shape[1], edited_patch.shape[0]) != (patch_width, patch_height):
        edited_patch = cv2.resize(edited_patch, (patch_width, patch_height), interpolation=cv2.INTER_LANCZOS4)

    # all-white mask: blend the entire patch
    mask = 255 * np.ones((patch_height, patch_width), dtype=np.uint8)

    center = ((x1 + x2) // 2, (y1 + y2) // 2)
    result = cv2.seamlessClone(edited_patch, original, mask, center, cv2.NORMAL_CLONE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, result)
    return out_path
