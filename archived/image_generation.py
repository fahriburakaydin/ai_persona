import torch
from diffusers import StableDiffusionPipeline
import tempfile

def generate_realistic_image(prompt: str) -> str:
    """
    Generates a realistic image based on the given prompt.
    Returns the local file path of the saved image.
    """
    model_id = "stabilityai/stable-diffusion-2-1"  # You can update this to a model fine-tuned for photorealism
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load the Stable Diffusion pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        revision="fp16" if device == "cuda" else None,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    pipe = pipe.to(device)
    
    # Generate the image using a reasonable guidance scale
    generated = pipe(prompt, guidance_scale=7.5)
    image = generated.images[0]
    
    # Save the generated image to a temporary file and return its path
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    image.save(temp_file.name)
    return temp_file.name

if __name__ == "__main__":
    prompt = input("Enter image prompt: ")
    path = generate_realistic_image(prompt)
    print(f"Generated image saved to: {path}")
