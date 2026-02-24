import sys
import os
sys.path.append('src')

from crop import crop_with_buffer, save_crop_metadata
from chatgpt_api import edit_image_with_api, blend_images_with_api
from blend import blend_patch_back
from composite import hard_paste


BLEND_PROMPT = (
    "The second image has an edited region pasted in. "
    "Seamlessly blend that region into the image so it matches the lighting, "
    "color, and texture of the surrounding area. Only modify pixels near the "
    "edit boundary. Keep everything else identical to the first image."
)


def _setup_paths(image_name, session_name, method):
    original = f"data/originals/{image_name}.png"
    patch_dir = f"data/patches/{image_name}"
    edited_dir = f"data/edited_patches/{image_name}"
    output_dir = f"data/outputs/{image_name}"
    for d in [patch_dir, edited_dir, output_dir]:
        os.makedirs(d, exist_ok=True)

    tag = f"{session_name}_{method}"
    return {
        "original": original,
        "patch": os.path.join(patch_dir, f"{tag}.png"),
        "meta": os.path.join(patch_dir, f"{tag}_meta.json"),
        "edited": os.path.join(edited_dir, f"{tag}_edited.png"),
        "output": os.path.join(output_dir, f"{tag}_result.png"),
        "spliced": os.path.join(output_dir, f"{tag}_spliced.png"),
    }


def _crop_and_edit(paths, session_name, prompt, x1, y1, x2, y2, padding, total_steps):
    # crop
    print(f"[1/{total_steps}] Cropping ({x1},{y1})-({x2},{y2}) padding={padding}px")
    bbox = crop_with_buffer(paths["original"], x1, y1, x2, y2, padding, paths["patch"])
    save_crop_metadata({
        "source_image": paths["original"],
        "original_bbox": [x1, y1, x2, y2],
        "buffered_bbox": list(bbox),
        "padding": padding,
        "patch_path": paths["patch"],
        "edited_patch_path": paths["edited"],
        "description": prompt,
        "session_name": session_name
    }, paths["meta"])
    print(f"       Patch: {paths['patch']} ({bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}px)")

    # edit
    print(f"[2/{total_steps}] Editing: '{prompt}'")
    edit_image_with_api(paths["patch"], prompt, paths["edited"])
    print(f"       Edited: {paths['edited']}")


def run_code_blend(image_name, session_name, prompt, x1, y1, x2, y2, padding):
    # crop -> edit -> poisson blend
    paths = _setup_paths(image_name, session_name, "code-blend")

    _crop_and_edit(paths, session_name, prompt, x1, y1, x2, y2, padding, total_steps=3)

    print(f"[3/3] Blending (Poisson)")
    blend_patch_back(paths["original"], paths["edited"], paths["meta"], paths["output"])
    print(f"       Output: {paths['output']}")

    print(f"\nDone! Result: {paths['output']}")
    return paths["output"]


def run_oneshot(image_name, session_name, prompt):
    # full image -> edit -> done
    paths = _setup_paths(image_name, session_name, "oneshot")

    print(f"[1/1] Editing full image: '{prompt}'")
    edit_image_with_api(paths["original"], prompt, paths["output"])
    print(f"       Output: {paths['output']}")

    print(f"\nDone! Result: {paths['output']}")
    return paths["output"]


def run_llm_blend(image_name, session_name, prompt, x1, y1, x2, y2, padding):
    # crop -> edit -> hard paste -> llm blend
    paths = _setup_paths(image_name, session_name, "llm-blend")

    _crop_and_edit(paths, session_name, prompt, x1, y1, x2, y2, padding, total_steps=4)

    print(f"[3/4] Hard-pasting edited patch")
    hard_paste(paths["original"], paths["edited"], paths["meta"], paths["spliced"])
    print(f"       Spliced: {paths['spliced']}")

    print(f"[4/4] LLM blending")
    blend_images_with_api(paths["original"], paths["spliced"], BLEND_PROMPT, paths["output"])
    print(f"       Output: {paths['output']}")

    print(f"\nDone! Result: {paths['output']}")
    return paths["output"]
