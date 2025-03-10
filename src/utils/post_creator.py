import os
from datetime import datetime, timedelta
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration

def interactive_post_creation(persona_name: str, display_name: str) -> None:
    """
    Handles the multi-turn dialogue for generating a post.
    This function collects all necessary inputs from the user,
    confirms the details, generates an image if needed, and then
    either posts immediately or schedules the post.
    """
    print("🤖 Lia: Let's create a new post together!")
    
    # 1. Immediate or Scheduled Post?
    post_type = input("🤖 Lia: Do you want this post to be immediate ('now') or scheduled? (now/scheduled): ").strip().lower()
    
    scheduled_time = None
    frequency = None
    if post_type == "scheduled":
        scheduled_time = input("🤖 Lia: At what time should I post it? (HH:MM): ").strip()
        frequency = input("🤖 Lia: Should I post this daily or just once? (daily/once): ").strip().lower()
    
    # 2. Image: Generate new or use an existing image?
    image_choice = input("🤖 Lia: Should I generate a new image or use an existing one? (generate/existing): ").strip().lower()
    
    image_source = None  # will eventually hold the image file path (local)
    if image_choice == "existing":
        image_source = input("🤖 Lia: Please provide the file path for the image: ").strip()
    else:
        # Ask if the user wants to provide a prompt, or have Lia choose one
        prompt_choice = input("🤖 Lia: Would you like to provide an image prompt, or should I choose one for inspiration? (provide/choose): ").strip().lower()
        image_prompt = None
        if prompt_choice == "provide":
            image_prompt = input("🤖 Lia: Please enter the image prompt: ").strip()
        else:
            # Default inspirational prompt; refine as needed later.
            image_prompt = "A stunning, ultra-realistic photograph that captures the essence of beauty and emotion."
            print(f"🤖 Lia: I'll use this prompt for inspiration: '{image_prompt}'")
        
        print("🤖 Lia: Generating image, please wait...")
        image_source = generate_image(image_prompt)
        if not image_source:
            print("🤖 Lia: I couldn't generate the image. Let's try again later.")
            return  # Exit the post creation process
    
    # 3. Caption for the Post
    caption_choice = input("🤖 Lia: Would you like to provide a caption or should I generate one? (provide/generate): ").strip().lower()
    caption = ""
    if caption_choice == "provide":
        caption = input("🤖 Lia: Please enter the caption for the post: ").strip()
    else:
        # Simple default caption; you can replace this with dynamic generation later.
        caption = f"New post by {display_name}! Stay tuned for more updates."
        print(f"🤖 Lia: I'll use this caption: '{caption}'")
    
    # 4. Confirmation of Post Details
    print("\n🤖 Lia: Here's what I've gathered:")
    print(f"    Post Type: {'Immediate' if post_type == 'now' else 'Scheduled'}")
    if post_type == "scheduled":
        print(f"    Scheduled Time: {scheduled_time}")
        print(f"    Frequency: {frequency}")
    print(f"    Image Source: {image_source}")
    print(f"    Caption: {caption}\n")
    
    confirm = input("🤖 Lia: Is this correct? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("🤖 Lia: Okay, let's cancel this post creation.")
        return
    
    # 5. Post or Schedule the Content
    if post_type == "now":
        ig_bot = InstagramIntegration(persona_name)
        if ig_bot.login():
            if os.path.exists(image_source):
                try:
                    # Use photo_upload for local files.
                    result = ig_bot.client.photo_upload(
                        path=image_source,
                        caption=caption,
                        extra_data={"disable_comments": False}
                    )
                    print("🤖 Lia: Post successful!", result)
                except Exception as e:
                    print("🤖 Lia: Failed to post due to:", e)
            else:
                try:
                    result = ig_bot.post_content(image_source, caption)
                    print("🤖 Lia: Post successful!", result)
                except Exception as e:
                    print("🤖 Lia: Failed to post due to:", e)
        else:
            print("🤖 Lia: Instagram login failed; cannot post right now.")
    else:
        # For scheduling, we assume schedule_post_job is available in lia_console.
        from src.tools.lia_console import schedule_post_job
        schedule_post_job(scheduled_time, frequency, image_source, caption)
        print("🤖 Lia: Your post has been scheduled.")
