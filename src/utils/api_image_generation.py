import requests
import time
import os
from dotenv import load_dotenv
from src.utils.logger import logger
from src.config import HUGGINGFACE_API_KEY_1, HUGGINGFACE_API_KEY_2, HUGGINGFACE_API_KEY_3

load_dotenv()

# List of API keys to rotate through
HUGGINGFACE_API_KEYS = [key for key in [HUGGINGFACE_API_KEY_1, HUGGINGFACE_API_KEY_2, HUGGINGFACE_API_KEY_3] if key]

if not HUGGINGFACE_API_KEYS:
    logger.error("No Hugging Face API keys found in the environment.")
    raise Exception("No Hugging Face API keys available.")

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"

def query(prompt: str, seed: int = 42, max_retries: int = 5, backoff_factor: float = 5.0) -> bytes:
    payload = {"inputs": prompt, "seed": seed}

    for key_index, api_key in enumerate(HUGGINGFACE_API_KEYS):
        logger.info(f"🌀 Using Hugging Face API key #{key_index + 1}")
        HEADERS = {"Authorization": f"Bearer {api_key}"}

        for attempt in range(max_retries):
            try:
                response = requests.post(API_URL, headers=HEADERS, json=payload)
            except Exception as e:
                logger.error("Request failed due to a connection error on attempt %d: %s", attempt + 1, e)
                time.sleep(backoff_factor)
                backoff_factor *= 2
                continue

            if response.status_code == 200:
                return response.content

            elif response.status_code == 503:
                logger.warning("Received 503 error. Attempt %d/%d. Retrying in %f seconds...", attempt + 1, max_retries, backoff_factor)
                time.sleep(backoff_factor)
                backoff_factor *= 2

            elif response.status_code == 402 or "monthly included credits" in response.text.lower():
                logger.warning("API key #%d quota exceeded. Switching to the next key...", key_index + 1)
                break  # Break retry loop, go to next key

            else:
                try:
                    error_message = response.json()
                except Exception:
                    error_message = response.text
                logger.error("Error in query with status %d: %s", response.status_code, error_message)
                raise Exception(f"Error: {error_message}")

    logger.error("All API keys exhausted or failed.")
    raise Exception("All Hugging Face API keys exhausted or failed.")

def generate_image(prompt: str, seed: int = 42) -> str:
    """
    Generates an image from the given prompt using Hugging Face's Inference API.
    Saves the resulting image into the /images folder and returns its file path.
    """
    image_data = query(prompt, seed=seed)

    images_folder = os.path.join(os.getcwd(), "images")
    os.makedirs(images_folder, exist_ok=True)

    filename = f"image_{int(time.time())}_{seed}.png"
    filepath = os.path.join(images_folder, filename)

    with open(filepath, "wb") as f:
        f.write(image_data)

    return filepath

if __name__ == "__main__":
    prompt = input("Enter image prompt: ")
    try:
        path = generate_image(prompt)
        print(f"Generated image saved to: {path}")
    except Exception as e:
        logger.error("Image generation failed: %s", e)
