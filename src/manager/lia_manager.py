import os
import time
from datetime import datetime, timedelta
from src.config import MIN_POST_GAP_HOURS
from src.utils.post_generation_agents import generate_weighted_post_plan
from src.utils.prompt_engineer import generate_technical_prompt
from src.utils.api_image_generation import generate_image
from src.utils.instagram_integration import InstagramIntegration

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
        """Generates a creative post plan, uses the expert prompt engineer for the technical prompt,
        and then asks for final approval before posting."""
        print("🤖 Lia (Manager): I've decided it's a good time for a new post based on our context.")
        conversation_context = self.persona.memory.retrieve_short_term_memory()
        plan = generate_weighted_post_plan(self.persona, conversation_context)
        print("🤖 Lia (Manager): My post plan is:")
        print("post_category: ", plan.get("post_category"))
        print("   Image Idea: ", plan.get("image_idea"))
        print("   Caption: ", plan.get("caption"))
        
        approval = input("🤖 Lia (Manager): Do you approve this post plan? (yes/no): ").strip().lower()
        if approval not in ["yes", "y"]:
            print("🤖 Lia (Manager): Post creation cancelled based on your feedback.")
            return

        post_category = plan.get("post_category", "general")
        technical_prompt = generate_technical_prompt(plan.get("image_idea", ""), post_category, self.persona)
        print("\n🤖 Lia (Manager): Generated technical prompt:")
        print("   ", technical_prompt)
        
        try:
            image_source = generate_image(technical_prompt)
        except Exception as e:
            print("🤖 Lia (Manager): Failed to generate image:", e)
            return
        if not image_source:
            print("🤖 Lia (Manager): Could not generate image. Post aborted.")
            return

        caption = plan.get("caption", "")
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
