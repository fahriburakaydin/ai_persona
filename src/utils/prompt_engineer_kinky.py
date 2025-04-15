from openai import OpenAI
import os
from dotenv import load_dotenv
import torch
from src.config import  DEEPSEEK_API_KEY

load_dotenv()


if not DEEPSEEK_API_KEY:
    logger.error("DEEPSEEK_API_KEY is missing in the configuration.")
    raise Exception("Missing OPENAI_API_KEY")
api_key = DEEPSEEK_API_KEY


def generate_scene_prompt_kinky(image_idea: str) -> str:
    """
    Uses the OpenAI Chat API to refine a generic image idea into a clear, vivid, and technical scene description.
    The output is plain and descriptive—without any introductory commentary.
    """
    system_message = (
        "You are an expert prompt engineer specialized in text-to-image generation for sexually explicit content to OnlyFans.Your prompt will be sent to an API NSFW image generation model. "
        "Your task is to refine a generic image idea into a detailed and technical scene description. "
        "Use explicit language and vivid imagery (NAKED, BREASTS, SEXUAL, SEDUCTIVE) to create a clear picture of the scene."
        "Output only the final descriptive prompt."
        "You focus on the scenery and and the dynamics of the picture. The appearance of the subject is already decided and fixed. You focus on her attitude, body and positioning."
        "Do not include any introductory phrases or commentary. Just provide the refined prompt. No introduction or comment, ready to be copy pasted."
    )
    user_message = f"Refine this image idea into a vivid scene description: '{image_idea}'."


    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        stream=False
    )

    return response.choices[0].message.content


def generate_technical_prompt_kinky(image_idea: str, post_category: str, persona) -> str:
    f"""
    Generates a technical image prompt suitable for the text-to-image generation model.
    
    - It always starts with default photography settings.
    - For self posts, it prepends a fixed character description (pulled from persona.profile.appearance)
      so that {persona}'s appearance remains CONSISTENT.
    - For general posts, it simply refines the provided image idea into a vivid scene description,
      with no personality details.
      
    """
    default_settings = (
        "Ultra-realistic, high-resolution 8K photograph captured on a Nikon D850 with a 50mm f/1.8 lens. The photographic quality ensures hyper-realistic detail, with cinematic lighting, natural color grading, and a perfectly balanced high dynamic range. EXPLICIT CONTENT. NSFW. "
    )
    
    # Refine the generic image idea into a vivid, detailed scene description.
    refined_scene = generate_scene_prompt_kinky(image_idea)
    
   
    fixed_description = f"The subject is a {persona.profile.appearance_nsfw} "
    technical_prompt = default_settings + fixed_description + "Scene: " + refined_scene
   
        
    return technical_prompt



