#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from blend import blend_patch_back
from crop import load_crop_metadata


def blend_edited_result(image_name, session_name):
    patch_dir = f"data/patches/{image_name}"
    meta_path = os.path.join(patch_dir, f"{session_name}_meta.json")

    print("=" * 70)
    print(f"Blending Result: {session_name}")
    print("=" * 70)

    meta = load_crop_metadata(meta_path)
    print(f"✓ Metadata loaded")

    original_path = meta['source_image']
    edited_patch_path = meta.get('edited_patch_path')

    if not edited_patch_path:
        edited_dir = f"data/edited_patches/{image_name}"
        edited_patch_path = os.path.join(edited_dir, f"{session_name}_edited.png")

    output_path = f"data/outputs/{image_name}/{session_name}_result.png"

    print(f"Source: {original_path}")
    print(f"Edited patch: {edited_patch_path}")
    print(f"Output: {output_path}")
    print(f"✓ Edited patch found")

    description = meta.get('description', 'Edit')
    print(f"\nBlending edited patch back into original...")
    print(f"Edit: {description}")

    result_path = blend_patch_back(
        original_path=original_path,
        edited_patch_path=edited_patch_path,
        meta_path=meta_path,
        out_path=output_path
    )

    print("\n" + "=" * 70)
    print("✓ BLEND SUCCESSFUL!")
    print("=" * 70)
    print(f"Result saved to: {result_path}")

    return result_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python blend_result.py <image_name> <session_name>")
        print("\nExample:")
        print("  python blend_result.py portrait sky_birds")
        sys.exit(1)

    image_name = sys.argv[1]
    session_name = sys.argv[2]

    blend_edited_result(image_name, session_name)


if __name__ == "__main__":
    main()
