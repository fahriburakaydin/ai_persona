import requests
import time
import os
from dotenv import load_dotenv
from src.utils.logger import logger 
from src.config import HUGGINGFACE_API_KEY_2 

load_dotenv()

if not HUGGINGFACE_API_KEY_2:
    logger.error("HUGGINGFACE_API_KEY_2 is not set in the environment.")
    raise Exception("Missing HUGGINGFACE_API_KEY_2 environment variable.")

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY_2}"}

def query(prompt: str, seed: int = 42, max_retries: int = 5, backoff_factor: float = 5.0) -> bytes:
    payload = {"inputs": prompt, "seed": seed}
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
            backoff_factor *= 2  # exponential backoff
        else:
            try:
                error_message = response.json()
            except Exception:
                error_message = response.text
            logger.error("Error in query with status %d: %s", response.status_code, error_message)
            raise Exception(f"Error: {error_message}")
    logger.error("Max retries exceeded. The model may still be loading or the service is unavailable.")
    raise Exception("Max retries exceeded.")

def generate_image(prompt: str, seed: int = 42) -> str:
    """
    Generates an image from the given prompt using Hugging Face's Inference API.
    Saves the resulting image into the /images folder and returns its file path.
    """
    image_data = query(prompt, seed=seed)
    
    # Define the images folder relative to the project root
    images_folder = os.path.join(os.getcwd(), "images")
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    
    # Create a unique filename using timestamp and seed
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