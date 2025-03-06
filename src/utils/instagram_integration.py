import os
import time
import random
import logging
import tempfile
import requests
from instagrapi import Client
from dotenv import load_dotenv

# Load environment variables at import time
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramIntegration:
    def __init__(self, persona_name: str):
        """
        Initialize a new InstagramIntegration instance for a specific persona.
        Each persona will have its own session file and device settings.
        """
        self.persona_name = persona_name
        self.client = Client()
        self._setup_device()
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        # Store session per persona (avoid re-login each time)
        self.session_file = f"{self.persona_name}_session.json"

    def _setup_device(self):
        """
        Mimic a real Android device to reduce the chance of being flagged.
        You can customize this device profile further if needed.
        """
        self.client.set_user_agent(
            "Instagram 289.0.0.30.120 Android (25/7.1.2; 380dpi; 1080x1920; unknown/Android; realme RMX1993; RMX1993; qcom; en_US; 367216753)"
        )
        self.client.set_device({
            "manufacturer": "realme",
            "model": "RMX1993",
            "android_version": 25,
            "android_release": "7.1.2"
        })

    def _human_delay(self, min_sec=1, max_sec=3):
        """
        Random delay between actions to mimic human behavior and avoid bot detection.
        Adjust min_sec and max_sec as needed.
        """
        time.sleep(random.uniform(min_sec, max_sec))

    def login(self) -> bool:
        """
        Attempts to log in using a cached session if available.
        Dumps session to a file if a fresh login is required.
        Returns True if login is successful, False otherwise.
        """
        try:
            # Reuse existing session if it exists
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                if self.client.user_id:
                    logger.info(f"[{self.persona_name}] Reused existing session.")
                    return True

            self._human_delay()
            logged_in = self.client.login(self.username, self.password)
            if not logged_in:
                logger.error(f"[{self.persona_name}] Login failed.")
                return False

            self.client.dump_settings(self.session_file)
            logger.info(f"[{self.persona_name}] New login successful.")
            return True

        except Exception as e:
            logger.error(f"[{self.persona_name}] Login error: {str(e)}")
            return False

    def post_content(self, image_url: str, caption: str) -> bool:
        """
        Downloads an image from a URL, enhances the caption with random emojis,
        and posts it to the persona's Instagram feed.
        Returns True if successful, False otherwise.
        """
        try:
            img_path = self._download_image(image_url)
            caption = self._enhance_caption(caption)
            self._human_delay(2, 5)

            self.client.photo_upload(
                path=img_path,
                caption=caption,
                extra_data={"disable_comments": False}
            )
            logger.info(f"[{self.persona_name}] Posted image with caption: {caption}")
            return True

        except Exception as e:
            logger.error(f"[{self.persona_name}] Post failed: {str(e)}")
            return False

    def comment_on_post(self, media_id: str, comment_text: str) -> bool:
        """
        Leaves a comment on a specific media post.
        media_id can be retrieved via client.media_id_from_link or other methods.
        Returns True if successful, False otherwise.
        """
        try:
            self._human_delay()
            self.client.media_comment(media_id, comment_text)
            logger.info(f"[{self.persona_name}] Commented on {media_id}: {comment_text}")
            return True
        except Exception as e:
            logger.error(f"[{self.persona_name}] Comment failed: {str(e)}")
            return False

    def like_post(self, media_id: str) -> bool:
        """
        Likes a specific media post by ID.
        Returns True if successful, False otherwise.
        """
        try:
            self._human_delay()
            self.client.media_like(media_id)
            logger.info(f"[{self.persona_name}] Liked post {media_id}")
            return True
        except Exception as e:
            logger.error(f"[{self.persona_name}] Like failed: {str(e)}")
            return False

    def follow_user(self, user_id: int) -> bool:
        """
        Follows a user by their numerical user_id.
        Returns True if successful, False otherwise.
        """
        try:
            self._human_delay()
            self.client.user_follow(user_id)
            logger.info(f"[{self.persona_name}] Followed user {user_id}")
            return True
        except Exception as e:
            logger.error(f"[{self.persona_name}] Follow failed: {str(e)}")
            return False

    def send_dm(self, user_id: int, message: str) -> bool:
        """
        Sends a direct message to a specific user.
        Returns True if successful, False otherwise.
        """
        try:
            self._human_delay()
            self.client.direct_send(message, [user_id])
            logger.info(f"[{self.persona_name}] DM sent to {user_id}: {message}")
            return True
        except Exception as e:
            logger.error(f"[{self.persona_name}] DM failed: {str(e)}")
            return False

    def _download_image(self, url: str) -> str:
        """
        Downloads an image from the given URL to a temporary file
        and returns the local file path.
        """
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Failed to download image.")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name

    def _enhance_caption(self, caption: str) -> str:
        """
        Randomly adds emojis to the caption to appear more 'human'.
        Customize or expand as you see fit.
        """
        emojis = ["🔥", "🌟", "💪", "✨", "🚀"]
        return f"{random.choice(emojis)} {caption} {random.choice(emojis)}"
