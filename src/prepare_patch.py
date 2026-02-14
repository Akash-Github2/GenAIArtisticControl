import sys
import os
import argparse
sys.path.append('src')

from crop import crop_with_buffer, save_crop_metadata, get_patch_subdirectory
from chatgpt_api import edit_image_with_api


def prepare_patch(image_name, x1, y1, x2, y2, padding, session_name, description="", use_api=False):
    original_path = f"data/originals/{image_name}.png"
    patch_dir = get_patch_subdirectory(original_path)

    edited_dir = f"data/edited_patches/{image_name}"
    os.makedirs(edited_dir, exist_ok=True)
    os.makedirs(f"data/outputs/{image_name}", exist_ok=True)

    patch_path = os.path.join(patch_dir, f"{session_name}.png")
    meta_path = os.path.join(patch_dir, f"{session_name}_meta.json")
    edited_patch_path = os.path.join(edited_dir, f"{session_name}_edited.png")

    print(f"Cropping ({x1},{y1})-({x2},{y2}) with {padding}px padding...")
    bbox = crop_with_buffer(original_path, x1, y1, x2, y2, padding, patch_path)
    print(f"  Patch: {patch_path} ({bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}px)")

    meta = {
        "source_image": original_path,
        "original_bbox": [x1, y1, x2, y2],
        "buffered_bbox": list(bbox),
        "padding": padding,
        "patch_path": patch_path,
        "edited_patch_path": edited_patch_path,
        "description": description,
        "session_name": session_name
    }
    save_crop_metadata(meta, meta_path)

    if use_api:
        if not description:
            print("Error: description required for --use-api")
            sys.exit(1)

        print(f"Sending to API: '{description}'")
        edit_image_with_api(patch_path, description, edited_patch_path)
        print(f"  Edited patch: {edited_patch_path}")
        print(f"\nNext: python src/blend_result.py {image_name} {session_name}")
    else:
        print(f"\nManual steps:")
        print(f"  1. Edit patch: {patch_path}")
        print(f"  2. Save to: {edited_patch_path}")
        print(f"  3. Run: python src/blend_result.py {image_name} {session_name}")

    return patch_path, edited_patch_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare an image patch for editing")
    parser.add_argument("image_name")
    parser.add_argument("x1", type=int)
    parser.add_argument("y1", type=int)
    parser.add_argument("x2", type=int)
    parser.add_argument("y2", type=int)
    parser.add_argument("padding", type=int)
    parser.add_argument("session_name")
    parser.add_argument("description", nargs="?", default="")
    parser.add_argument("--use-api", action="store_true")

    args = parser.parse_args()
    prepare_patch(
        args.image_name, args.x1, args.y1, args.x2, args.y2,
        args.padding, args.session_name, args.description, args.use_api
    )
