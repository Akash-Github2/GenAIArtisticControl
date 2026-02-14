import sys
import os
sys.path.append('src')

from blend import blend_patch_back
from crop import load_crop_metadata


def blend_edited_result(image_name, session_name):
    patch_dir = f"data/patches/{image_name}"
    meta_path = os.path.join(patch_dir, f"{session_name}_meta.json")

    meta = load_crop_metadata(meta_path)
    original_path = meta['source_image']
    edited_patch_path = meta.get('edited_patch_path')

    if not edited_patch_path:
        edited_dir = f"data/edited_patches/{image_name}"
        edited_patch_path = os.path.join(edited_dir, f"{session_name}_edited.png")

    output_path = f"data/outputs/{image_name}/{session_name}_result.png"

    print(f"Blending {session_name}...")
    print(f"  Source: {original_path}")
    print(f"  Edited patch: {edited_patch_path}")

    result_path = blend_patch_back(
        original_path=original_path,
        edited_patch_path=edited_patch_path,
        meta_path=meta_path,
        out_path=output_path
    )

    print(f"  Result: {result_path}")
    return result_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/blend_result.py <image_name> <session_name>")
        sys.exit(1)

    blend_edited_result(sys.argv[1], sys.argv[2])
