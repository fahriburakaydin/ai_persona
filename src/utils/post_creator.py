import os
import re
from datetime import datetime, timedelta
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration

def validate_time(time_str: str) -> bool:
    """Validate that time_str is in HH:MM 24-hour format."""
    pattern = r'^(?:[01]\d|2[0-3]):[0-5]\d$'
    return re.match(pattern, time_str) is not None

def interactive_post_creation(persona_name: str, display_name: str) -> None:
    """
    Handles the multi-turn dialogue for generating a post.
    This function collects all necessary inputs from the user,
    confirms the details, generates an image if needed, and then
    either posts immediately or schedules the post.
    
    You can type "back" at any prompt to return to the previous step.
    For the image, you can choose to generate, use an existing file/URL,
    or use a random image from picsum.photos.
    """
    print("🤖 Lia: Let's create a new post together!")
    
    data = {}
    step = 1
    while step <= 6:
        if step == 1:
            ans = input("🤖 Lia: Do you want this post to be immediate ('now') or scheduled? (now/scheduled): ").strip().lower()
            if ans == "back":
                print("🤖 Lia: Already at the first step.")
                continue
            if ans not in ["now", "scheduled"]:
                print("🤖 Lia: Please answer with 'now' or 'scheduled'.")
                continue
            data['post_type'] = ans
            step += 1
            continue

        if step == 2:
            if data['post_type'] == "scheduled":
                ans = input("🤖 Lia: At what time should I post it? (HH:MM, 24-hour format): ").strip()
                if ans.lower() == "back":
                    step -= 1
                    continue
                if not validate_time(ans):
                    print("🤖 Lia: The time format seems off. Please use HH:MM (e.g., '10:00').")
                    continue
                data['scheduled_time'] = ans
                ans2 = input("🤖 Lia: Should I post this daily or just once? (daily/once): ").strip().lower()
                if ans2 == "back":
                    continue
                if ans2 not in ["daily", "once"]:
                    print("🤖 Lia: Please answer with 'daily' or 'once'.")
                    continue
                data['frequency'] = ans2
            step += 1
            continue

        if step == 3:
            ans = input("🤖 Lia: Should I generate a new image, use an existing one, or pick a random image? (generate/existing/random): ").strip().lower()
            if ans == "back":
                step -= 1
                continue
            if ans not in ["generate", "existing", "random"]:
                print("🤖 Lia: Please answer with 'generate', 'existing', or 'random'.")
                continue
            data['image_choice'] = ans
            step += 1
            continue

        if step == 4:
            if data['image_choice'] == "existing":
                ans = input("🤖 Lia: Please provide the image (URL or full local file path): ").strip()
                if ans.lower() == "back":
                    step -= 1
                    continue
                if ans.startswith("http"):
                    data['image_source'] = ans
                elif os.path.exists(ans):
                    data['image_source'] = ans
                else:
                    print("🤖 Lia: I can't find that file. Please check the path or provide a valid URL.")
                    continue
            elif data['image_choice'] == "random":
                # Use a random image from picsum.photos
                data['image_source'] = "https://picsum.photos/1080/1080"
                print("🤖 Lia: I'll use a random image from picsum.photos.")
            else:
                # Generate a new image.
                ans = input("🤖 Lia: Would you like to provide an image prompt, or should I generate one for you? (provide/generate): ").strip().lower()
                if ans == "back":
                    step -= 1
                    continue
                if ans not in ["provide", "generate"]:
                    print("🤖 Lia: Please answer with 'provide' or 'generate'.")
                    continue
                data['prompt_choice'] = ans
                if ans == "provide":
                    ans2 = input("🤖 Lia: Please enter the image prompt: ").strip()
                    if ans2.lower() == "back":
                        continue
                    data['image_prompt'] = ans2
                else:
                    generated_prompt = persona.generate_response("Generate an inspiring image prompt for an Instagram post.")
                    print(f"🤖 Lia: I'll use this generated prompt: '{generated_prompt}'")
                    data['image_prompt'] = generated_prompt
                print("🤖 Lia: Generating image, please wait...")
                try:
                    image_path = generate_image(data['image_prompt'])
                except Exception as e:
                    print(f"🤖 Lia: I encountered an error during image generation: {e}")
                    return
                if not image_path:
                    print("🤖 Lia: I couldn't generate the image. Let's try again later.")
                    return
                data['image_source'] = image_path
            step += 1
            continue

        if step == 5:
            ans = input("🤖 Lia: Would you like to provide a caption or should I generate one? (provide/generate): ").strip().lower()
            if ans == "back":
                step -= 1
                continue
            if ans not in ["provide", "generate"]:
                print("🤖 Lia: Please answer with 'provide' or 'generate'.")
                continue
            data['caption_choice'] = ans
            if ans == "provide":
                ans2 = input("🤖 Lia: Please enter the caption for the post: ").strip()
                if ans2.lower() == "back":
                    continue
                data['caption'] = ans2
            else:
                generated_caption = persona.generate_response("Generate a creative caption for an Instagram post.")
                print(f"🤖 Lia: I'll use this generated caption: '{generated_caption}'")
                data['caption'] = generated_caption
            step += 1
            continue

        if step == 6:
            print("\n🤖 Lia: Here's what I've gathered:")
            print(f"    Post Type: {data.get('post_type')}")
            if data.get('post_type') == "scheduled":
                print(f"    Scheduled Time: {data.get('scheduled_time')}")
                print(f"    Frequency: {data.get('frequency')}")
            print(f"    Image Source: {data.get('image_source')}")
            print(f"    Caption: {data.get('caption')}\n")
            ans = input("🤖 Lia: Is this correct? (yes/no/back): ").strip().lower()
            if ans == "back":
                step -= 1
                continue
            if ans not in ["yes", "y"]:
                print("🤖 Lia: Okay, let's cancel this post creation.")
                return
            step += 1
            continue

    # Execute the post creation.
    if data.get('post_type') == "now":
        ig_bot = InstagramIntegration(persona_name)
        if ig_bot.login():
            if data.get('image_source').startswith("http"):
                try:
                    result = ig_bot.post_content(data.get('image_source'), data.get('caption'))
                    print("🤖 Lia: Post successful!", result)
                except Exception as e:
                    print("🤖 Lia: Failed to post due to:", e)
            elif os.path.exists(data.get('image_source')):
                try:
                    result = ig_bot.client.photo_upload(
                        path=data.get('image_source'),
                        caption=data.get('caption'),
                        extra_data={"disable_comments": False}
                    )
                    print("🤖 Lia: Post successful!", result)
                except Exception as e:
                    print("🤖 Lia: Failed to post due to:", e)
            else:
                print("🤖 Lia: The image source is invalid.")
        else:
            print("🤖 Lia: Instagram login failed; cannot post right now.")
    else:
        from src.tools.lia_console import schedule_post_job
        schedule_post_job(data.get('scheduled_time'), data.get('frequency'), data.get('image_source'), data.get('caption'), persona_name)
        print("🤖 Lia: Your post has been scheduled.")
