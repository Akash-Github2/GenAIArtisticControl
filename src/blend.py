#!/usr/bin/env python3

from PIL import Image, ImageFilter
import json
import os
import numpy as np


def blend_patch_back(original_path, edited_patch_path, meta_path, out_path, blur_radius=None):
    """Blend edited patch back into original image using soft masking."""
    # Load metadata
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    bx1, by1, bx2, by2 = meta['buffered_bbox']
    padding = meta['padding']

    # Load images
    original = Image.open(original_path).convert("RGBA")
    edited_patch = Image.open(edited_patch_path).convert("RGBA")

    # Resize patch if needed
    patch_width = bx2 - bx1
    patch_height = by2 - by1
    if edited_patch.size != (patch_width, patch_height):
        edited_patch = edited_patch.resize((patch_width, patch_height), Image.Resampling.LANCZOS)

    # Create soft mask
    if blur_radius is None:
        blur_radius = padding
    mask = create_soft_mask(patch_width, patch_height, padding, blur_radius)

    # Blend
    original_region = original.crop((bx1, by1, bx2, by2))
    blended_region = Image.composite(edited_patch, original_region, mask)

    # Paste back
    result = original.copy()
    result.paste(blended_region, (bx1, by1), mask)

    # Save
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result.save(out_path, 'PNG')

    return out_path


def create_soft_mask(width, height, padding, blur_radius=None):
    """Create soft alpha mask with gradient in buffer zone."""
    if blur_radius is None:
        blur_radius = padding

    # Create mask array
    mask_array = np.zeros((height, width), dtype=np.uint8)

    # Center region (full opacity)
    cx1, cy1 = padding, padding
    cx2, cy2 = width - padding, height - padding

    if cx2 > cx1 and cy2 > cy1:
        mask_array[cy1:cy2, cx1:cx2] = 255

    # Gradient in buffer zones
    y_coords, x_coords = np.mgrid[0:height, 0:width]

    dist_left = np.maximum(0, cx1 - x_coords)
    dist_right = np.maximum(0, x_coords - (cx2 - 1))
    dist_top = np.maximum(0, cy1 - y_coords)
    dist_bottom = np.maximum(0, y_coords - (cy2 - 1))

    outside_x = np.logical_or(x_coords < cx1, x_coords >= cx2)
    outside_y = np.logical_or(y_coords < cy1, y_coords >= cy2)

    h_dist = np.where(outside_x, np.minimum(dist_left, dist_right), 0)
    v_dist = np.where(outside_y, np.minimum(dist_top, dist_bottom), 0)

    min_dist = np.maximum(h_dist, v_dist)
    min_dist = np.clip(min_dist, 0, padding)
    alpha = (255 * (1 - min_dist / padding)).astype(np.uint8)

    mask_array = np.where(mask_array == 0, alpha, mask_array)

    # Convert to image and blur
    mask = Image.fromarray(mask_array, mode='L')
    if blur_radius > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    return mask
