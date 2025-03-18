import os
import time
import logging
from datetime import datetime, timedelta
from src.config import MIN_POST_GAP_HOURS
from src.utils.post_generation_agents import generate_weighted_post_plan
from src.utils.prompt_engineer import generate_technical_prompt
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration
from src.utils.post_tracker import log_post_draft, update_post_status, get_all_posts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info("🤖 Lia (Manager): I've decided it's a good time for a new post based on our context.")
        conversation_context = self.persona.memory.retrieve_short_term_memory()
        plan = generate_weighted_post_plan(self.persona, conversation_context)
        logger.info("🤖 Lia (Manager): My post plan is:")
        logger.info("   Post Category: %s", plan.get("post_category"))
        logger.info("   Image Idea: %s", plan.get("image_idea"))
        logger.info("   Caption: %s", plan.get("caption"))
        
        approval = input("🤖 Lia (Manager): Do you approve this post plan? (yes/no): ").strip().lower()
        if approval not in ["yes", "y"]:
            logger.info("🤖 Lia (Manager): Post creation cancelled based on your feedback.")
            return

        post_category = plan.get("post_category", "general")
        technical_prompt = generate_technical_prompt(plan.get("image_idea", ""), post_category, self.persona)
        logger.info("🤖 Lia (Manager): Generated technical prompt:")
        logger.info("   %s", technical_prompt)
        
        try:
            image_source = generate_image(technical_prompt, seed=42)
        except Exception as e:
            logger.error("🤖 Lia (Manager): Failed to generate image: %s", e)
            return
        if not image_source:
            logger.error("🤖 Lia (Manager): Could not generate image. Post aborted.")
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
        logger.info("🤖 Lia (Manager): Draft post logged with ID %s", draft_id)
        
        # Final approval for posting.
        logger.info("🤖 Lia (Manager): Here is the final post proposal:")
        logger.info("    Image Source: %s", image_source)
        logger.info("    Caption: %s", caption)
        final_confirm = input("🤖 Lia (Manager): Do you approve the final post? (yes/no): ").strip().lower()
        if final_confirm not in ["yes", "y"]:
            logger.info("🤖 Lia (Manager): Post creation cancelled based on your review.")
            return
        
        ig_bot = InstagramIntegration(self.persona_name)
        if ig_bot.login():
            max_attempts = 3
            result = None
            for attempt in range(max_attempts):
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
                        logger.error("🤖 Lia (Manager): Invalid image source.")
                        return
                    # Break out of loop if successful
                    break
                except Exception as e:
                    logger.error("🤖 Lia (Manager): Instagram posting attempt %d failed: %s", attempt + 1, e)
                    time.sleep(30)  # Wait a bit before retrying
            else:
                logger.error("🤖 Lia (Manager): All attempts to post on Instagram failed.")
                return

            logger.info("🤖 Lia (Manager): Post successful! %s", result)
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
            logger.info("🤖 Lia (Manager): DB updated with post details, after the insta.")
        else:
            logger.error("🤖 Lia (Manager): Instagram login failed; cannot post.")

    def run(self):
        """Continuously checks if a post should be created and creates one if needed."""
        logger.info("🤖 Lia (Manager): Autonomous posting activated.")
        while True:
            if self.should_post():
                self.create_post_autonomously()
            time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    from src.utils.openai_integration import LiaLama
    persona = LiaLama("src/profiles/lia_lama.json", debug=True)
    first_name = persona.profile.name.split()[0]
    persona_name = first_name.lower()
    display_name = first_name
    manager = LiaManager(persona, persona_name, display_name)
    manager.create_post_autonomously()
