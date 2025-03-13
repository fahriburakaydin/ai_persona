import openai
import os
from dotenv import load_dotenv
import torch

load_dotenv()

def generate_scene_prompt(image_idea: str) -> str:
    """
    Uses the OpenAI Chat API to refine a generic image idea into a clear, vivid, and technical scene description.
    The output is plain and descriptive—without any introductory commentary.
    """
    system_message = (
        "You are an expert prompt engineer specialized in text-to-image generation. "
        "Your task is to refine a generic image idea into a detailed and technical scene description. "
        "Output only the final descriptive prompt."
    )
    user_message = f"Refine this image idea into a vivid scene description: '{image_idea}'."
    
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

def generate_technical_prompt(image_idea: str, post_category: str, persona) -> str:
    """
    Generates a technical image prompt suitable for the text-to-image generation model.
    
    - It always starts with default photography settings.
    - For self posts, it prepends a fixed character description (pulled from persona.profile.appearance)
      so that Lia's appearance remains consistent.
    - For general posts, it simply refines the provided image idea into a vivid scene description,
      with no personality details.
      
    A fixed seed can be used later in the image-generation call for further consistency.
    """
    default_settings = (
        "Ultra-realistic, high-resolution 8K photograph captured on a Nikon D850 with a 50mm f/1.8 lens. "
    )
    
    # Refine the generic image idea into a vivid, detailed scene description.
    refined_scene = generate_scene_prompt(image_idea)
    
    if post_category.lower() == "self":
        # Use the fixed appearance from the profile (from the centralized "appearance" field).
        fixed_description = f"The subject is a {persona.profile.appearance} "
        technical_prompt = default_settings + fixed_description + "Scene: " + refined_scene
    else:
        technical_prompt = default_settings + "Scene: " + refined_scene
        
    return technical_prompt
