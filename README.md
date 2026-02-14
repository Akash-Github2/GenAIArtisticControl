# Modular GenAI Image Editing (UCLA Capstone)

A pipeline for making targeted edits to specific regions of an image using GenAI, without affecting the rest of the composition. Instead of passing an entire image to GenAI and risking unintended changes, this tool isolates a region, edits just that patch, and blends it back seamlessly. It's an experiment to see if modular GenAI image editing will produce better results than re-prompting the full image.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-proj-...
```

## Usage

### End-to-end (single command)

```bash
python src/pipeline.py portrait 40 40 290 290 30 sky_birds "Add a flock of birds flying across the sky"
```

### Manual path (step by step)

```bash
# 1. crop the patch
python src/prepare_patch.py portrait 40 40 290 290 30 sky_birds "Add birds"

# 2. manually edit the patch (upload to ChatGPT, save result to the path shown)

# 3. blend it back
python src/blend_result.py portrait sky_birds
```

Arguments: `<image_name> <x1> <y1> <x2> <y2> <padding> <session_name> <prompt>`

- `image_name` — filename (without .png) in `data/originals/`
- `x1 y1 x2 y2` — pixel coordinates of the region to edit
- `padding` — extra pixels around the region for smooth blending
- `session_name` — name for this edit (used for all intermediate files)

## How it works

```
original image
    → [crop] region + padding buffer
    → [edit] send patch to gpt-image-1, resize result back to original dimensions
    → [blend] composite edited patch over original using soft gradient mask
    → output image
```

## Data layout

```
data/
  originals/            source images (put your PNGs here)
  patches/<name>/       cropped patches + metadata JSON
  edited_patches/<name>/  edited versions
  outputs/<name>/       final blended results
```
