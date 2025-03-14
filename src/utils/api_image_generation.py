import requests
import tempfile
import time
import os
from dotenv import load_dotenv

load_dotenv()

hf_api_key = os.getenv("HUGGINGFACE_API_KEY_2")

API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"
HEADERS = {"Authorization": f"Bearer {hf_api_key}"}  # Replace with your token

def query(prompt: str, seed: int = 42, max_retries: int = 5, backoff_factor: float = 5.0) -> bytes:
    """
    Sends a prompt to the Hugging Face Inference API and returns the binary image data.
    Includes a seed parameter for consistency.
    Retries on 503 errors with exponential backoff.
    """
    payload = {"inputs": prompt, "seed": seed}
    for attempt in range(max_retries):
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            print(f"Received 503 error. Attempt {attempt+1}/{max_retries}. Retrying in {backoff_factor} seconds...")
            time.sleep(backoff_factor)
            backoff_factor *= 2  # exponential backoff
        else:
            try:
                error_message = response.json()
            except Exception:
                error_message = response.text
            raise Exception(f"Error: {error_message}")
    raise Exception("Max retries exceeded. The model may still be loading or the service is unavailable.")

def generate_image(prompt: str, seed: int = 42) -> str:
    """
    Generates an image from the given prompt using Hugging Face's Inference API.
    Saves the resulting image to a temporary file and returns its file path.
    The fixed seed parameter ensures consistent outputs.
    """
    image_data = query(prompt, seed=seed) 
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    with open(temp_file.name, "wb") as f:
        f.write(image_data)
    return temp_file.name

if __name__ == "__main__":
    prompt = input("Enter image prompt: ")
    try:
        path = generate_image(prompt)
        print(f"Generated image saved to: {path}")
    except Exception as e:
        print(str(e))
