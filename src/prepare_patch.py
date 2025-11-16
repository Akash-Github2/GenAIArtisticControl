#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from crop import crop_with_buffer, save_crop_metadata, get_patch_subdirectory


def prepare_patch_for_editing(image_name, x1, y1, x2, y2, padding, session_name, edit_description=""):
    original_path = f"data/originals/{image_name}.png"
    patch_dir = get_patch_subdirectory(original_path)

    edited_dir = f"data/edited_patches/{image_name}"
    output_dir = f"data/outputs/{image_name}"
    os.makedirs(edited_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    patch_path = os.path.join(patch_dir, f"{session_name}.png")
    meta_path = os.path.join(patch_dir, f"{session_name}_meta.json")
    edited_patch_path = os.path.join(edited_dir, f"{session_name}_edited.png")

    print("=" * 70)
    print(f"Preparing Patch: {session_name}")
    print("=" * 70)
    print(f"Source image: {original_path}")
    print(f"Region: ({x1}, {y1}) to ({x2}, {y2})")
    print(f"Region size: {x2-x1}x{y2-y1} pixels")
    print(f"Padding: {padding}px")
    if edit_description:
        print(f"Description: {edit_description}")

    print(f"\nCropping patch...")
    bbox = crop_with_buffer(original_path, x1, y1, x2, y2, padding, patch_path)

    print(f"✓ Patch cropped successfully")
    print(f"  Buffered bbox: {bbox}")
    print(f"  Patch size: {bbox[2]-bbox[0]}x{bbox[3]-bbox[1]} pixels")

    meta = {
        "source_image": original_path,
        "original_bbox": [x1, y1, x2, y2],
        "buffered_bbox": list(bbox),
        "padding": padding,
        "patch_path": patch_path,
        "edited_patch_path": edited_patch_path,
        "description": edit_description,
        "session_name": session_name
    }
    save_crop_metadata(meta, meta_path)
    print(f"✓ Metadata saved")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print(f"1. Open patch for editing:")
    print(f"   {patch_path}")
    print(f"\n2. Upload to ChatGPT/DALL-E and apply this edit:")
    if edit_description:
        print(f"   '{edit_description}'")
    else:
        print(f"   [Your edit description here]")
    print(f"\n3. Download edited version and save to:")
    print(f"   {edited_patch_path}")
    print(f"\n4. Run blending script:")
    print(f"   python blend_result.py {image_name} {session_name}")
    print("=" * 70)

    return patch_path, edited_patch_path


def main():
    if len(sys.argv) < 8:
        print("Usage: python prepare_patch.py <image_name> <x1> <y1> <x2> <y2> <padding> <session_name> [description]")
        print("\nExample:")
        print('  python prepare_patch.py portrait 40 40 400 350 50 sky_birds "Add birds to sky"')
        sys.exit(1)

    image_name = sys.argv[1]
    x1, y1, x2, y2 = map(int, sys.argv[2:6])
    padding = int(sys.argv[6])
    session_name = sys.argv[7]
    description = " ".join(sys.argv[8:]) if len(sys.argv) > 8 else ""

    prepare_patch_for_editing(image_name, x1, y1, x2, y2, padding, session_name, description)


if __name__ == "__main__":
    main()
