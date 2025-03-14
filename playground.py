# playground.py
from src.utils.post_tracker import log_post_draft, update_post_status, get_all_posts
import json

# Example post details from your logs:
post_details = {
    "timestamp": "2025-03-14T11:21:39",
    "caption": "Sometimes, grace and strength reside in the quiet moments. Who else finds power in subtlety? 😌✨ #StrengthInSoftness #GoldenHourGlow",
    "image_idea": "A luminous portrait of a woman with warm, golden blonde hair flowing around her face, accentuated by natural sunlight...",
    "dynamic_scene": "Create an image of a woman captured in a soft-focus portrait, bathed in warm, golden sunlight...",
    "technical_prompt": "Ultra-realistic, high-resolution 8K photograph captured on a Nikon D850 with a 50mm f/1.8 lens. The subject is a [ ... ] Scene: Create an image of a woman captured in a soft-focus portrait, bathed in warm, golden sunlight streaming through a window to her left. ...",
    "image_source": r"C:\Users\fahri\github\personal\ai_persona\src\utils\images\tmpn0e4md4v.png",
    "post_category": "self",
    "result": {
        "pk": "3588070019821839774",
        "code": "DHLYqwwtaWe"
    }
}

# Step 1: Log the draft post (before final approval)
draft_data = {
    "timestamp": post_details["timestamp"],
    "caption": post_details["caption"],
    "image_idea": post_details["image_idea"],
    "dynamic_scene": post_details["dynamic_scene"],
    "technical_prompt": post_details["technical_prompt"],
    "image_source": "",  # Not set in the draft
    "post_category": post_details["post_category"],
    "insta_post_id": "",  # Not set in the draft
    "insta_code": ""      # Not set in the draft
}

draft_id = log_post_draft(draft_data)
print(f"Draft post logged with ID: {draft_id}")

# Step 2: Simulate final posting by updating the draft with Instagram details.
updated_data = {
    "insta_post_id": post_details["result"]["pk"],
    "insta_code": post_details["result"]["code"],
    "image_source": post_details["image_source"],
    "caption": post_details["caption"]
}

update_post_status(draft_id, updated_data)
print(f"Draft with ID {draft_id} updated as posted.")

# Step 3: Retrieve and display all posts from the database.
posts = get_all_posts()
print("Final posts logged:")
for post in posts:
    print(post)
