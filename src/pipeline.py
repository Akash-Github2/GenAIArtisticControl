import sys
import os
import argparse
sys.path.append('src')

from crop import crop_with_buffer, save_crop_metadata, get_patch_subdirectory
from chatgpt_api import edit_image_with_api
from blend import blend_patch_back


def run_pipeline(image_name, x1, y1, x2, y2, padding, session_name, prompt):
    original_path = f"data/originals/{image_name}.png"
    patch_dir = get_patch_subdirectory(original_path)
    edited_dir = f"data/edited_patches/{image_name}"
    output_dir = f"data/outputs/{image_name}"
    os.makedirs(edited_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    patch_path = os.path.join(patch_dir, f"{session_name}.png")
    meta_path = os.path.join(patch_dir, f"{session_name}_meta.json")
    edited_patch_path = os.path.join(edited_dir, f"{session_name}_edited.png")
    output_path = os.path.join(output_dir, f"{session_name}_result.png")

    # 1. crop
    print(f"[1/3] Cropping ({x1},{y1})-({x2},{y2}) padding={padding}px")
    bbox = crop_with_buffer(original_path, x1, y1, x2, y2, padding, patch_path)
    save_crop_metadata({
        "source_image": original_path,
        "original_bbox": [x1, y1, x2, y2],
        "buffered_bbox": list(bbox),
        "padding": padding,
        "patch_path": patch_path,
        "edited_patch_path": edited_patch_path,
        "description": prompt,
        "session_name": session_name
    }, meta_path)
    print(f"      Patch: {patch_path} ({bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}px)")

    # 2. api edit
    print(f"[2/3] Editing: '{prompt}'")
    edit_image_with_api(patch_path, prompt, edited_patch_path)
    print(f"      Edited: {edited_patch_path}")

    # 3. blend
    print(f"[3/3] Blending back into original")
    blend_patch_back(original_path, edited_patch_path, meta_path, output_path)
    print(f"      Output: {output_path}")

    print(f"\nDone! Result: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-end modular image editing")
    parser.add_argument("image_name")
    parser.add_argument("x1", type=int)
    parser.add_argument("y1", type=int)
    parser.add_argument("x2", type=int)
    parser.add_argument("y2", type=int)
    parser.add_argument("padding", type=int)
    parser.add_argument("session_name")
    parser.add_argument("prompt")

    args = parser.parse_args()
    run_pipeline(
        args.image_name, args.x1, args.y1, args.x2, args.y2,
        args.padding, args.session_name, args.prompt
    )
