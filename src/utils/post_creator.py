import os
from datetime import datetime
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration
from src.utils.post_generation_agents import generate_weighted_post_plan
from src.utils.post_tracker import log_post_draft, update_post_status
from src.utils.prompt_engineer import generate_technical_prompt

def interactive_post_creation(persona_name: str, display_name: str, persona) -> None:
    """
    Interactive post creation flow:
      1. Lia asks if you already have a post plan.
         - If yes: you manually supply the image (URL or local path) and caption.
         - If no: Lia generates a post plan (image idea, caption, post_category) using conversation context.
      2. If Lia generates the plan, she uses it to produce a technical prompt and generate the image.
      3. The final post proposal (image source and caption) is shown.
      4. Upon your final confirmation, Lia posts to Instagram.
    """
    # Step 1: Determine if a plan is provided or generated.
    plan_choice = input("🤖 Lia: Do you already have a post plan? (yes/no): ").strip().lower()
    
    if plan_choice in ["yes", "y"]:
        # Manual entry: User provides the image and caption.
        image_source = input("🤖 Lia: Please provide the image (URL or local file path): ").strip()
        if not (image_source.startswith("http") or os.path.exists(image_source)):
            print("🤖 Lia: The image source is invalid. Post creation cancelled.")
            return
        caption = input("🤖 Lia: Please provide the caption for the post: ").strip()
        post_category = "self"  # Defaulting to 'self'; adjust if needed.
        # In manual mode, we don't generate a dynamic scene or technical prompt.
    else:
        # Automated process: Lia generates a post plan using conversation context.
        print("🤖 Lia: Let me think about a great post idea based on our conversation...")
        conversation_context = persona.memory.retrieve_short_term_memory()
        plan = generate_weighted_post_plan(persona, conversation_context)
        print("🤖 Lia: Here's the post plan I came up with:")
        print("   Post Category:", plan.get("post_category"))
        print("   Image Idea:", plan.get("image_idea"))
        print("   Caption:", plan.get("caption"))
        
        approval = input("🤖 Lia: Do you approve this post plan? (yes/no): ").strip().lower()
        if approval not in ["yes", "y"]:
            feedback = input("🤖 Lia: Please provide feedback to refine the plan: ").strip()
            refined_context = conversation_context + " Feedback: " + feedback
            plan = generate_weighted_post_plan(persona, refined_context)
            print("🤖 Lia: Here's the refined post plan:")
            print("   Post Category:", plan.get("post_category"))
            print("   Image Idea:", plan.get("image_idea"))
            print("   Caption:", plan.get("caption"))
            approval = input("🤖 Lia: Do you approve this refined plan? (yes/no): ").strip().lower()
            if approval not in ["yes", "y"]:
                print("🤖 Lia: Okay, post creation cancelled.")
                return
        
        post_category = plan.get("post_category", "general")
        # Generate a technical prompt using the image idea.
        technical_prompt = generate_technical_prompt(plan.get("image_idea", ""), post_category, persona)
        print("\n🤖 Lia: Generated technical prompt:")
        print("   ", technical_prompt)
        
        try:
            image_source = generate_image(technical_prompt, seed=42)
        except Exception as e:
            print("🤖 Lia: Failed to generate image:", e)
            return
        if not image_source:
            print("🤖 Lia: Could not generate image. Post aborted.")
            return
        caption = plan.get("caption", "")
    
    # Log the post draft into the database before final approval.
    current_timestamp = datetime.now().isoformat()
    # For automated posts, we extract the dynamic scene from the technical prompt if available.
    dynamic_scene = ""
    if plan_choice not in ["yes", "y"]:
        dynamic_scene = technical_prompt.split("Scene: ", 1)[-1] if "Scene: " in technical_prompt else ""
    draft_details = {
        "timestamp": current_timestamp,
        "caption": caption,
        "image_idea": plan.get("image_idea") if plan_choice not in ["yes", "y"] else "User Provided",
        "dynamic_scene": dynamic_scene,
        "technical_prompt": technical_prompt if plan_choice not in ["yes", "y"] else "",
        "image_source": image_source,  
        "post_category": post_category,
        "insta_post_id": "",
        "insta_code": "",
        "is_posted": 0
    }
    draft_id = log_post_draft(draft_details)
    print("🤖 Lia: Draft post logged with ID", draft_id)
    
    # Step 4: Final Post Proposal and Confirmation
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
            try:
                if image_source.startswith("http"):
                    result = ig_bot.post_content(image_source, caption)
                elif os.path.exists(image_source):
                    result = ig_bot.client.photo_upload(
                        path=image_source,
                        caption=caption,
                        extra_data={"disable_comments": False}
                    )
                else:
                    print("🤖 Lia: The image source is invalid.")
                    return
                print("🤖 Lia: Post successful!", result)
                # Update DB with Instagram post details.
                insta_post_id = result.get("pk", "") if isinstance(result, dict) else ""
                insta_code = result.get("code", "") if isinstance(result, dict) else ""
                updated_data = {
                    "insta_post_id": insta_post_id,
                    "insta_code": insta_code,
                    "is_posted": 1
                }
                update_post_status(draft_id, updated_data)
                print("🤖 Lia: Database updated with post details.")
            except Exception as e:
                print("🤖 Lia: Failed to post due to:", e)
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
