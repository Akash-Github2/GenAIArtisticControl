# Modular GenAI Image Editing (UCLA Capstone)

A pipeline for making targeted edits to specific regions of an image using GenAI, without affecting the rest of the composition. Instead of passing an entire image to GenAI and risking unintended changes, this tool isolates a region, edits just that patch, and blends it back seamlessly.

The project implements three different editing pipelines to compare how much LLM involvement produces the best results:

- **code-blend** — Crop a region, edit it with the API, blend it back using Poisson blending (cv2.seamlessClone)
- **oneshot** — Send the full image to the API with a prompt, let the model handle everything
- **llm-blend** — Crop and edit like code-blend, but use a second API call to have the model do the blending instead of code

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

All three pipelines run through a single entry point:

```bash
# code-blend: crop -> api edit -> poisson blend
python src/run_pipeline.py code-blend portrait sky_birds "add a flock of birds flying in the sky" \
  --x1 0 --y1 0 --x2 400 --y2 350 --padding 30

# oneshot: full image -> api edit (no coordinates needed)
python src/run_pipeline.py oneshot portrait sky_birds "add a flock of birds flying in the sky"

# llm-blend: crop -> api edit -> hard paste -> api blend
python src/run_pipeline.py llm-blend portrait sky_birds "add a flock of birds flying in the sky" \
  --x1 0 --y1 0 --x2 400 --y2 350 --padding 30
```

Results go to `data/outputs/<image_name>/` with the method name in the filename, so you can compare them side by side.

### Arguments

- `image_name` — filename (without .png) in `data/originals/`
- `session_name` — name for this edit (used for all intermediate and output files)
- `prompt` — what to edit
- `--x1 --y1 --x2 --y2` — pixel coordinates of the region to edit (code-blend and llm-blend only)
- `--padding` — extra pixels around the region for blending context (code-blend and llm-blend only)

## How it works

### code-blend
```
original -> crop region with padding -> send patch to gpt-image-1 -> resize back -> poisson blend into original -> output
```

### oneshot
```
original -> send full image to gpt-image-1 -> resize back -> output
```

### llm-blend
```
original -> crop region with padding -> send patch to gpt-image-1 -> resize back -> hard paste into original -> send original + spliced to gpt-image-1 for blending -> resize back -> output
```

## Data layout

```
data/
  originals/              source images (put your PNGs here)
  patches/<name>/         cropped patches + metadata JSON
  edited_patches/<name>/  edited versions from the API
  outputs/<name>/         final results
```

## Project structure

```
src/
  run_pipeline.py     CLI entry point for all three pipelines
  pipelines.py        pipeline orchestration (run_code_blend, run_oneshot, run_llm_blend)
  crop.py             cropping with padding buffer + metadata
  blend.py            poisson blending (cv2.seamlessClone)
  composite.py        hard paste (no blending, used as intermediate step)
  chatgpt_api.py      OpenAI API calls (single-image edit + two-image blend)
```
