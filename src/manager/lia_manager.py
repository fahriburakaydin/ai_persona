import os
import time
from datetime import datetime, timedelta
from src.config import MIN_POST_GAP_HOURS
from src.utils.post_generation_agents import generate_weighted_post_plan
from src.utils.prompt_engineer import generate_technical_prompt
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration
from src.utils.post_tracker import log_post_draft, update_post_status, get_all_posts
from datetime import datetime

class LiaManager:
    def __init__(self, persona, persona_name: str, display_name: str):
        self.persona = persona
        self.persona_name = persona_name
        self.display_name = display_name
        self.last_post_time = None  # Track when the last post was made

    def should_post(self) -> bool:
        """Decide whether Lia should create a new post based on the minimum time gap."""
        now = datetime.now()
        if self.last_post_time is None:
            return True
        gap = now - self.last_post_time
        return gap >= timedelta(hours=MIN_POST_GAP_HOURS)

    def create_post_autonomously(self):
        print("🤖 Lia (Manager): I've decided it's a good time for a new post based on our context.")
        conversation_context = self.persona.memory.retrieve_short_term_memory()
        plan = generate_weighted_post_plan(self.persona, conversation_context)
        print("🤖 Lia (Manager): My post plan is:")
        print("   Post Category:", plan.get("post_category"))
        print("   Image Idea:", plan.get("image_idea"))
        print("   Caption:", plan.get("caption"))
        
        approval = input("🤖 Lia (Manager): Do you approve this post plan? (yes/no): ").strip().lower()
        if approval not in ["yes", "y"]:
            print("🤖 Lia (Manager): Post creation cancelled based on your feedback.")
            return

        post_category = plan.get("post_category", "general")
        technical_prompt = generate_technical_prompt(plan.get("image_idea", ""), post_category, self.persona)
        print("\n🤖 Lia (Manager): Generated technical prompt:")
        print("   ", technical_prompt)
        
        try:
            image_source = generate_image(technical_prompt, seed=42)
        except Exception as e:
            print("🤖 Lia (Manager): Failed to generate image:", e)
            return
        if not image_source:
            print("🤖 Lia (Manager): Could not generate image. Post aborted.")
            return

        caption = plan.get("caption", "")
        # Extract dynamic scene part from the technical prompt (after "Scene: ")
        dynamic_scene = technical_prompt.split("Scene: ", 1)[-1]
        
        # Log the draft post immediately with is_posted = 0.
        current_timestamp = datetime.now().isoformat()
        draft_details = {
            "timestamp": current_timestamp,
            "caption": caption,
            "image_idea": plan.get("image_idea"),
            "dynamic_scene": dynamic_scene,
            "technical_prompt": technical_prompt,
            "image_source": image_source,  
            "post_category": post_category,
            "insta_post_id": "",
            "insta_code": "",
            "is_posted": 0
        }
        draft_id = log_post_draft(draft_details)
        print(f"🤖 Lia (Manager): Draft post logged with ID {draft_id}")
        
        # Final approval for posting.
        print("\n🤖 Lia (Manager): Here is the final post proposal:")
        print("    Image Source:", image_source)
        print("    Caption:", caption)
        final_confirm = input("🤖 Lia (Manager): Do you approve the final post? (yes/no): ").strip().lower()
        if final_confirm not in ["yes", "y"]:
            print("🤖 Lia (Manager): Post creation cancelled based on your review.")
            return
        
        ig_bot = InstagramIntegration(self.persona_name)
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
                    print("🤖 Lia (Manager): Invalid image source.")
                    return
                print("🤖 Lia (Manager): Post successful!", result)
                self.last_post_time = datetime.now()

                # Extract key Instagram fields from the result.
                insta_post_id = result.get("pk", "") if isinstance(result, dict) else ""
                insta_code = result.get("code", "") if isinstance(result, dict) else ""
                updated_data = {
                    "insta_post_id": insta_post_id,
                    "insta_code": insta_code,
                    "is_posted": 1
                }
                update_post_status(draft_id, updated_data)
                print("🤖 Lia (Manager): Draft updated with post details.")
            except Exception as e:
                print("🤖 Lia (Manager): Failed to post due to:", e)
        else:
            print("🤖 Lia (Manager): Instagram login failed; cannot post.")


    def run(self):
        """Continuously checks if a post should be created and creates one if needed."""
        print("🤖 Lia (Manager): Autonomous posting activated.")
        while True:
            if self.should_post():
                self.create_post_autonomously()
            time.sleep(5)  # Check every 10 minutes

if __name__ == "__main__":
    from src.utils.openai_integration import LiaLama
    persona = LiaLama("src/profiles/lia_lama.json", debug=True)
    first_name = persona.profile.name.split()[0]
    persona_name = first_name.lower()
    display_name = first_name
    manager = LiaManager(persona, persona_name, display_name)
    manager.create_post_autonomously()
