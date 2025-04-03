# src/manager/lia_manager.py

import os
import time
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.openai_integration import LiaLama
    from src.utils.instagram_integration import InstagramIntegration

from src.config import MIN_POST_GAP_HOURS, FULL_AUTONOMOUS_MODE
from src.utils.post_generation_agents import generate_weighted_post_plan
from src.utils.prompt_engineer import generate_technical_prompt
from src.utils.api_image_generation import generate_image
from src.utils.post_tracker import log_post_draft, update_post_status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LiaManager:
    """
    Manages Lia's autonomous posting schedule and process on Instagram.
    """
    def __init__(self, persona: 'LiaLama', ig_bot: 'InstagramIntegration', persona_name: str):
        """
        Initializes the Lia Manager.

        Args:
            persona: The LiaLama persona instance containing memory, profile, etc.
            ig_bot: An initialized InstagramIntegration instance.
            persona_name: The character's name (used primarily for logging/identification).
        """
        self.persona = persona
        self.persona_name = persona_name
        self.ig_bot = ig_bot
        self.last_post_time = None  # Track when the last post was made
        logger.info(f"🤖 Lia Manager initialized for {self.persona_name}.")

    def _get_last_post_time_from_db(self):
        from src.utils.post_tracker import get_latest_post_timestamp
        self.last_post_time = get_latest_post_timestamp()
        if self.last_post_time:
            logger.info(f"🤖 Last post time loaded from DB: {self.last_post_time}")
        else:
            logger.info("🤖 No previous post time found in DB. Assuming first post.")
        return self.last_post_time

    def should_post(self) -> bool:
        """Decide whether Lia should create a new post based on the minimum time gap."""
        if self.last_post_time is None:
            self._get_last_post_time_from_db()
            if self.last_post_time is None:
                logger.info("🤖 No previous post time found. Okay to post.")
                return True

        now = datetime.now()
        gap = now - self.last_post_time
        should = gap >= timedelta(hours=MIN_POST_GAP_HOURS)
        if not should:
            logger.info(f"🤖 Post check: Too soon. Last post: {self.last_post_time}. Need {MIN_POST_GAP_HOURS} hours.")
        return should

    def create_post_autonomously(self):
        """Handles the process of creating and publishing a single post."""
        logger.info("🤖 Lia (Manager): Initiating autonomous post creation sequence.")

        # Use the injected ig_bot instance directly
        if not self.ig_bot.login():
            logger.info("🤖 Lia (Manager): Attempting Instagram login...")
            if not self.ig_bot.login():
                logger.error("🤖 Lia (Manager): Instagram login failed; cannot post.")
                return
            logger.info("🤖 Lia (Manager): Instagram login successful.")

        logger.info(f"🤖 Lia (Debug): FULL_AUTONOMOUS_MODE is {FULL_AUTONOMOUS_MODE}")

        # 1. Get Context & Generate Plan
        try:
            conversation_context = self.persona.memory.retrieve_short_term_memory()
            logger.info("🤖 Lia (Manager): Retrieved short-term memory for context.")
            plan = generate_weighted_post_plan(self.persona, conversation_context)
            logger.info("🤖 Lia (Manager): Generated post plan:")
            logger.info(f"   Post Category: {plan.get('post_category')}")
            logger.info(f"   Image Idea: {plan.get('image_idea')}")
            logger.info(f"   Caption: {plan.get('caption')}")
        except Exception as e:
            logger.error(f"🤖 Lia (Manager): Failed to generate post plan: {e}", exc_info=True)
            return

        # 2. Approval (Optional)
        if not FULL_AUTONOMOUS_MODE:
            try:
                approval = input("🤖 Lia (Manager): Do you approve this post plan? (yes/no): ").strip().lower()
                if approval not in ["yes", "y"]:
                    logger.info("🤖 Lia (Manager): Post creation cancelled by user (plan stage).")
                    return
            except EOFError:
                logger.warning("🤖 Lia (Manager): Running in non-interactive mode. Cannot ask for plan approval.")
                if not FULL_AUTONOMOUS_MODE:
                    logger.warning("🤖 Lia (Manager): Cancelling post due to non-interactive mode and FULL_AUTONOMOUS_MODE=False.")
                    return
        if FULL_AUTONOMOUS_MODE:
            approval = "yes"

        # 3. Generate Image Prompt & Image
        try:
            post_category = plan.get("post_category", "general")
            image_idea = plan.get("image_idea", "A thoughtful abstract image")
            technical_prompt = generate_technical_prompt(image_idea, post_category, self.persona)
            logger.info("🤖 Lia (Manager): Generated technical prompt:")
            logger.info(f"   {technical_prompt}")
            image_source = generate_image(technical_prompt)
            if not image_source:
                logger.error("🤖 Lia (Manager): Image generation returned no source. Post aborted.")
                return
            logger.info(f"🤖 Lia (Manager): Image generated successfully: {image_source}")
        except Exception as e:
            logger.error(f"🤖 Lia (Manager): Failed during image generation: {e}", exc_info=True)
            return

        # 4. Prepare Caption & Log Draft
        caption = plan.get("caption", f"Sharing some thoughts today. #{post_category}")
        dynamic_scene = technical_prompt.split("Scene: ", 1)[-1] if "Scene: " in technical_prompt else "N/A"

        draft_details = {
            "timestamp": datetime.now().isoformat(),
            "caption": caption,
            "image_idea": image_idea,
            "dynamic_scene": dynamic_scene,
            "technical_prompt": technical_prompt,
            "image_source": image_source,
            "post_category": post_category,
            "insta_post_id": "",
            "insta_code": "",
            "is_posted": 0  # Mark as not posted yet
        }
        try:
            draft_id = log_post_draft(draft_details)
            logger.info(f"🤖 Lia (Manager): Draft post logged with internal ID {draft_id}")
        except Exception as e:
            logger.error(f"🤖 Lia (Manager): Failed to log post draft: {e}", exc_info=True)
            logger.warning("🤖 Lia (Manager): Proceeding without draft log entry.")
            draft_id = None

        # 5. Final Approval (Optional)
        logger.info("🤖 Lia (Manager): Final post proposal review:")
        logger.info(f"    Image Source: {image_source}")
        logger.info(f"    Caption: {caption}")
        if not FULL_AUTONOMOUS_MODE:
            try:
                final_confirm = input("🤖 Lia (Manager): Post final proposal? (yes/no): ").strip().lower()
                if final_confirm not in ["yes", "y"]:
                    logger.info("🤖 Lia (Manager): Post creation cancelled by user (final stage).")
                    return
            except EOFError:
                logger.warning("🤖 Lia (Manager): Running in non-interactive mode. Cannot ask for final approval.")
                if not FULL_AUTONOMOUS_MODE:
                    logger.warning("🤖 Lia (Manager): Cancelling post due to non-interactive mode and FULL_AUTONOMOUS_MODE=False.")
                    return

        # 6. Post to Instagram
        
        if self.ig_bot.login():
            max_attempts = 3
            result = None
            for attempt in range(max_attempts):
                try:
                    if image_source.startswith("http"):
                        result = ig_bot.post_content(image_source, caption)
                    elif os.path.exists(image_source):
                        result = self.ig_bot.client.photo_upload(
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

        # 7. Update Post Status & Internal State
        logger.info(f"🤖 Lia (Manager): Post published successfully! Result: {post_result}")
        self.last_post_time = datetime.now()  # Update last post time on success

        # Assuming post_result is a dictionary-like object similar to instagrapi's Media:
        insta_post_id = getattr(result, 'pk', '') if result else ''
        insta_code = getattr(result, 'code', '') if result else ''

        if draft_id and (insta_post_id or insta_code):
            updated_data = {
                "insta_post_id": str(insta_post_id),
                "insta_code": insta_code,
                "is_posted": 1
            }
            try:
                update_post_status(draft_id, updated_data)
                logger.info(f"🤖 Lia (Manager): DB updated for draft ID {draft_id} with Instagram post details.")
            except Exception as e:
                logger.error(f"🤖 Lia (Manager): Failed to update post status in DB for draft ID {draft_id}: {e}", exc_info=True)
        elif draft_id:
            logger.warning(f"🤖 Lia (Manager): Instagram post successful, but no ID/Code found in result. DB not updated for draft {draft_id}.")
            update_post_status(draft_id, {"is_posted": 1, "insta_post_id": "[unknown]", "insta_code": "[unknown]"})

    def run(self):
        """Continuously checks if a post should be created and creates one if needed."""
        logger.info(f"🤖 Lia Manager ({self.persona_name}): Autonomous posting process starting.")
        self._get_last_post_time_from_db()

        while True:
            try:
                if self.should_post():
                    self.create_post_autonomously()
                time.sleep(600)  # Check every 10 minutes
            except KeyboardInterrupt:
                logger.info("🤖 Lia Manager: Shutdown signal received. Exiting posting loop.")
                break
            except Exception as e:
                logger.critical(f"🤖 Lia Manager: Unhandled exception in main loop: {e}", exc_info=True)
                logger.info("🤖 Lia Manager: Sleeping for 5 minutes after error before retrying.")
                time.sleep(300)


if __name__ == "__main__":
    print("--- Running Lia Manager Standalone Example ---")
    import sys
    from pathlib import Path

    # Adjust the Python path so that modules can be imported correctly.
    project_root = Path(__file__).resolve().parents[2]
    sys.path.append(str(project_root))
    print(f"Added project root to path: {project_root}")

    try:
        from src.utils.openai_integration import LiaLama
        from src.utils.instagram_integration import InstagramIntegration
        from src.utils.chroma_factory import get_chroma_client_and_embedder

        print("Initializing ChromaDB client and embedder...")
        client, embedder = get_chroma_client_and_embedder()
        print("ChromaDB setup complete.")

        print("Initializing LiaLama persona...")
        persona = LiaLama(
            profile_path="src/profiles/lia_lama.json",
            debug=True
        )
        persona_name = persona.profile.name.split()[0].lower()
        print(f"LiaLama persona '{persona_name}' initialized.")

        print("Initializing Instagram Integration...")
        ig_bot = InstagramIntegration(persona_name)
        print("Initializing LiaManager...")
        manager = LiaManager(persona=persona, ig_bot=ig_bot, persona_name=persona_name)
        print("LiaManager initialized. Starting run loop...")
        manager.run()

    except ImportError as e:
        print("\nERROR: Failed to import necessary modules.")
        print("Ensure you are running this from the correct directory or have set up your Python path properly.")
        print(f"PYTHONPATH might need to include: {project_root}")
        print(f"Import error details: {e}")
    except FileNotFoundError as e:
        print("\nERROR: File not found. Likely the persona profile is missing or path is incorrect.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during setup: {e}")
        import traceback
        traceback.print_exc()

    print("--- Lia Manager Standalone Example Finished ---")
