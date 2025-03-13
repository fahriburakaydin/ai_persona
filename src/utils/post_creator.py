import os
import re
from datetime import datetime, timedelta
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration
from src.utils.post_generation_agents import generate_post_plan, generate_image_prompt  # Helper functions (see below)

def validate_time(time_str: str) -> bool:
    """Validate that time_str is in HH:MM 24-hour format."""
    pattern = r'^(?:[01]\d|2[0-3]):[0-5]\d$'
    return re.match(pattern, time_str) is not None

def interactive_post_creation(persona_name: str, display_name: str, persona) -> None:
    """
    New autonomous post creation flow.
    Lia first generates a structured post plan (with an image idea and a caption) from the conversation context.
    Then, if an image is to be generated, she refines the image idea into a detailed image prompt.
    Before generating the image, she presents the prompt for your review and feedback.
    Finally, she executes the post (immediately or scheduled) using the refined inputs.
    """
    print("🤖 Lia: Let me think about a great post idea based on our conversation...")
    
    # Retrieve conversation context from memory.
    conversation_context = persona.memory.retrieve_short_term_memory()
    # Generate a structured post plan using a helper agent.
    plan = generate_post_plan(persona, conversation_context)
    print("🤖 Lia: Here's the post plan I came up with:")
    print("   Image Idea:", plan.get("image_idea"))
    print("   Caption:", plan.get("caption"))
    
    approval = input("🤖 Lia: Do you approve this plan? (yes/no): ").strip().lower()
    if approval not in ["yes", "y"]:
        feedback = input("🤖 Lia: Please provide feedback to refine the plan: ").strip()
        refined_context = conversation_context + " Feedback: " + feedback
        plan = generate_post_plan(persona, refined_context)
        print("🤖 Lia: Here's the refined plan:")
        print("   Image Idea:", plan.get("image_idea"))
        print("   Caption:", plan.get("caption"))
        approval = input("🤖 Lia: Do you approve this refined plan? (yes/no): ").strip().lower()
        if approval not in ["yes", "y"]:
            print("🤖 Lia: Okay, post creation cancelled.")
            return

    # Decide image source.
    image_option = input("🤖 Lia: Should I generate a new image or use an existing one? (type 'generate', 'existing', or 'random'): ").strip().lower()
    if image_option == "existing":
        image_source = input("🤖 Lia: Please provide the image (URL or local file path): ").strip()
        if not (image_source.startswith("http") or os.path.exists(image_source)):
            print("🤖 Lia: The image source is invalid. Post creation cancelled.")
            return
    elif image_option == "random":
        image_source = "https://picsum.photos/1080/1080"
        print("🤖 Lia: I'll use a random image from picsum.photos.")
    else:
        # Use the image idea from the plan to generate a detailed image prompt.
        image_prompt = generate_image_prompt(persona, plan.get("image_idea", ""), conversation_context)
        print("\n🤖 Lia: I generated the following image prompt for the post:")
        print("   ", image_prompt)
        # Allow you to review and provide feedback.
        while True:
            prompt_feedback = input("🤖 Lia: Does this image prompt look good? (Type 'yes' to approve, or provide feedback to refine it): ").strip()
            if prompt_feedback.lower() in ["yes", "y"]:
                break
            else:
                image_prompt = persona.generate_response(
                    f"Refine the following image prompt based on this feedback: {prompt_feedback}. Prompt: {image_prompt}"
                )
                print("🤖 Lia: Here's the refined image prompt:")
                print("   ", image_prompt)
        print("🤖 Lia: Generating image, please wait...")
        try:
            image_source = generate_image(image_prompt)
        except Exception as e:
            print(f"🤖 Lia: I encountered an error during image generation: {e}")
            return
        if not image_source:
            print("🤖 Lia: I couldn't generate the image. Let's try again later.")
            return

    # Use the caption from the plan.
    caption = plan.get("caption", "")
    print("\n🤖 Lia: Here is the proposed caption:")
    print("   ", caption)
    # Allow you to refine the caption.
    while True:
        caption_feedback = input("🤖 Lia: Do you approve this caption? (Type 'yes' to accept, or provide feedback to refine it): ").strip()
        if caption_feedback.lower() in ["yes", "y"]:
            break
        else:
            caption = persona.generate_response(
                f"Refine the caption for an Instagram post based on this feedback: {caption_feedback}. Original caption: {caption}"
            )
            print("🤖 Lia: Here's the refined caption:")
            print("   ", caption)
    
    # Final confirmation.
    print("\n🤖 Lia: Here's the final post proposal:")
    print("    Image Source:", image_source)
    print("    Caption:", caption)
    final_confirm = input("🤖 Lia: Should I go ahead and post this? (Type 'now' to post immediately, 'schedule' to schedule, or 'cancel' to abort): ").strip().lower()
    if final_confirm == "cancel":
        print("🤖 Lia: Post creation cancelled.")
        return
    elif final_confirm == "now":
        ig_bot = InstagramIntegration(persona_name)
        if ig_bot.login():
            if image_source.startswith("http"):
                try:
                    result = ig_bot.post_content(image_source, caption)
                    print("🤖 Lia: Post successful!", result)
                except Exception as e:
                    print("🤖 Lia: Failed to post due to:", e)
            elif os.path.exists(image_source):
                try:
                    result = ig_bot.client.photo_upload(
                        path=image_source,
                        caption=caption,
                        extra_data={"disable_comments": False}
                    )
                    print("🤖 Lia: Post successful!", result)
                except Exception as e:
                    print("🤖 Lia: Failed to post due to:", e)
            else:
                print("🤖 Lia: The image source is invalid.")
        else:
            print("🤖 Lia: Instagram login failed; cannot post now.")
    elif final_confirm == "schedule":
        time_str = input("🤖 Lia: At what time should I schedule the post? (HH:MM): ").strip()
        frequency = input("🤖 Lia: Should I schedule it daily or just once? (daily/once): ").strip().lower()
        from src.tools.lia_console import schedule_post_job
        result = schedule_post_job(time_str, frequency, image_source, caption, persona_name)
        print("🤖 Lia:", result)
    else:
        print("🤖 Lia: Unrecognized option. Post creation cancelled.")
