import cv2
import json
import os
import numpy as np


def blend_patch_back(original_path, edited_patch_path, meta_path, out_path):
    # poisson blending via cv2.seamlessClone
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    bx1, by1, bx2, by2 = meta['buffered_bbox']
    ox1, oy1, ox2, oy2 = meta['original_bbox']

    original = cv2.imread(original_path)
    edited_patch = cv2.imread(edited_patch_path)

    patch_width = bx2 - bx1
    patch_height = by2 - by1
    if (edited_patch.shape[1], edited_patch.shape[0]) != (patch_width, patch_height):
        edited_patch = cv2.resize(edited_patch, (patch_width, patch_height), interpolation=cv2.INTER_LANCZOS4)

    # actual padding per side (clamped at image edges)
    pad_left = ox1 - bx1
    pad_top = oy1 - by1
    pad_right = bx2 - ox2
    pad_bottom = by2 - oy2

    # mask: white = edit region, black = padding buffer
    mask = np.zeros((patch_height, patch_width), dtype=np.uint8)
    inner_y1 = min(pad_top, patch_height // 2)
    inner_x1 = min(pad_left, patch_width // 2)
    inner_y2 = max(patch_height - pad_bottom, patch_height // 2 + 1)
    inner_x2 = max(patch_width - pad_right, patch_width // 2 + 1)
    mask[inner_y1:inner_y2, inner_x1:inner_x2] = 255

    center = ((bx1 + bx2) // 2, (by1 + by2) // 2)
    result = cv2.seamlessClone(edited_patch, original, mask, center, cv2.NORMAL_CLONE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, result)
    return out_path
