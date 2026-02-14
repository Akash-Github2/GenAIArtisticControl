import os
import base64
import time
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, APIConnectionError

load_dotenv()

EDIT_MODEL = "gpt-image-1"
MAX_RETRIES = 3


def get_api_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Add it to .env or export it.")
    return OpenAI(api_key=api_key)


def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        return img.size


def pick_api_size(width, height):
    # gpt-image-1 only supports these fixed sizes
    if width == height:
        return "1024x1024"
    elif width > height:
        return "1536x1024"
    else:
        return "1024x1536"


def resize_to(image_path, target_size, output_path=None):
    with Image.open(image_path) as img:
        if img.size == target_size:
            return image_path
        resized = img.resize(target_size, Image.Resampling.LANCZOS)
        out = output_path or image_path
        resized.save(out, 'PNG')
        return out


def edit_image_with_api(image_path, prompt, output_path, max_retries=MAX_RETRIES):
    # Send patch to gpt-image-1 for editing, then resize result back to original dimensions
    client = get_api_client()
    original_size = get_image_dimensions(image_path)
    api_size = pick_api_size(*original_size)

    last_error = None
    for attempt in range(max_retries):
        try:
            with open(image_path, "rb") as f:
                response = client.images.edit(
                    model=EDIT_MODEL,
                    image=f,
                    prompt=prompt,
                    size=api_size,
                )

            image_bytes = base64.b64decode(response.data[0].b64_json)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            # resize back to original patch dimensions
            resize_to(output_path, original_size, output_path)
            return output_path

        except (RateLimitError, APIConnectionError) as e:
            last_error = e
            wait = 2 ** attempt
            print(f"  Retrying in {wait}s... ({e})")
            time.sleep(wait)

        except APIError as e:
            last_error = e
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  API error, retrying in {wait}s... ({e})")
            time.sleep(wait)

    raise ValueError(f"Failed after {max_retries} attempts: {last_error}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python src/chatgpt_api.py <image_path> <prompt> <output_path>")
        sys.exit(1)

    try:
        result = edit_image_with_api(sys.argv[1], sys.argv[2], sys.argv[3])
        print(f"Saved to: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
