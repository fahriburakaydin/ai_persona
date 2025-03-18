# src/utils/instagram_integration.py
import os
import time
import random
import logging
import tempfile
import requests
from instagrapi import Client
from dotenv import load_dotenv
from src.utils.logger import logger

load_dotenv()

class InstagramIntegration:
    def __init__(self, persona_name: str):
        self.persona_name = persona_name
        self.client = Client()
        self._setup_device()
        self.username = os.getenv("INSTAGRAM_USERNAME")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.session_file = f"{self.persona_name}_session.json"

    def _setup_device(self):
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
        time.sleep(random.uniform(min_sec, max_sec))

    def login(self) -> bool:
        try:
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                if self.client.user_id:
                    logger.info("[%s] Reused existing session.", self.persona_name)
                    return True
            self._human_delay()
            logged_in = self.client.login(self.username, self.password)
            if not logged_in:
                logger.error("[%s] Login failed.", self.persona_name)
                return False
            self.client.dump_settings(self.session_file)
            logger.info("[%s] New login successful.", self.persona_name)
            return True
        except Exception as e:
            logger.error("[%s] Login error: %s", self.persona_name, e)
            return False

    def post_content(self, image_url: str, caption: str) -> bool:
        try:
            img_path = self._download_image(image_url)
            caption = self._enhance_caption(caption)
            self._human_delay(2, 5)
            self.client.photo_upload(
                path=img_path,
                caption=caption,
                extra_data={"disable_comments": False}
            )
            logger.info("[%s] Posted image with caption: %s", self.persona_name, caption)
            return True
        except Exception as e:
            logger.error("[%s] Post failed: %s", self.persona_name, e)
            return False

    def comment_on_post(self, media_id: str, comment_text: str) -> bool:
        try:
            self._human_delay()
            self.client.media_comment(media_id, comment_text)
            logger.info("[%s] Commented on %s: %s", self.persona_name, media_id, comment_text)
            return True
        except Exception as e:
            logger.error("[%s] Comment failed: %s", self.persona_name, e)
            return False

    def like_post(self, media_id: str) -> bool:
        try:
            self._human_delay()
            self.client.media_like(media_id)
            logger.info("[%s] Liked post %s", self.persona_name, media_id)
            return True
        except Exception as e:
            logger.error("[%s] Like failed: %s", self.persona_name, e)
            return False

    def follow_user(self, user_id: int) -> bool:
        try:
            self._human_delay()
            self.client.user_follow(user_id)
            logger.info("[%s] Followed user %s", self.persona_name, user_id)
            return True
        except Exception as e:
            logger.error("[%s] Follow failed: %s", self.persona_name, e)
            return False

    def send_dm(self, user_id: int, message: str) -> bool:
        try:
            self._human_delay()
            self.client.direct_send(message, [user_id])
            logger.info("[%s] DM sent to %s: %s", self.persona_name, user_id, message)
            return True
        except Exception as e:
            logger.error("[%s] DM failed: %s", self.persona_name, e)
            return False

    def _download_image(self, url: str) -> str:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError("Failed to download image.")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            logger.error("[%s] Download image failed: %s", self.persona_name, e)
            raise

    def _enhance_caption(self, caption: str) -> str:
        emojis = ["🔥", "🌟", "💪", "✨", "🚀"]
        return f"{random.choice(emojis)} {caption} {random.choice(emojis)}"
