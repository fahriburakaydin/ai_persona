import json
from src.utils.post_tracker import log_post

# Example post details from your logs:
post_details = {
    "timestamp": "2025-03-14T11:21:39",
    "caption": "Sometimes, grace and strength reside in the quiet moments. Who else finds power in subtlety? 😌✨ #StrengthInSoftness #GoldenHourGlow",
    "image_idea": "A luminous portrait of a woman with warm, golden blonde hair flowing around her face, accentuated by natural sunlight...",
    "dynamic_scene": "Create an image of a woman captured in a soft-focus portrait, bathed in warm, golden sunlight...",  # Extracted from technical prompt
    "technical_prompt": "Ultra-realistic, high-resolution 8K photograph captured on a Nikon D850 with a 50mm f/1.8 lens. The subject is a [ ... ] Scene: Create an image of a woman captured in a soft-focus portrait, bathed in warm, golden sunlight streaming through a window to her left. ...",  # Full technical prompt
    "image_source": "C:\\Users\\fahri\\AppData\\Local\\Temp\\tmpn0e4md4v.png",
    "post_category": "self",
    "result": {
        "pk": "3588070019821839774",
        "code": "DHLYqwwtaWe"
    }
}

# Log the post details into your SQLite database.
log_post(post_details)
