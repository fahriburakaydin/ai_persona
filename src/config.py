# src/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Credentials loaded from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
HUGGINGFACE_API_KEY_1 = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_KEY_2 = os.getenv("HUGGINGFACE_API_KEY_2")
HUGGINGFACE_API_KEY_3 = os.getenv("HUGGINGFACE_API_KEY_3")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Posting mode: "fixed" or "dynamic"
POSTING_MODE = "dynamic"
FIXED_POSTING_INTERVAL = "18:00"  # used if POSTING_MODE == "fixed"

# Content mix ratios (adjust as needed)
SELF_CONTENT_RATIO = 0.4  
THEMATIC_CONTENT_RATIO = 0.6

# Self-image handling mode: "preapproved", "generated", or "hybrid"
SELF_IMAGE_MODE = "hybrid"

# Engagement learning settings
ENGAGEMENT_UPDATE_INTERVAL = 24  # in hours
LEARNING_RATE = 0.1

# Autonomous posting triggers
MIN_POST_GAP_HOURS = 12        # minimum hours between posts
ENGAGEMENT_TRIGGER_THRESHOLD = 0.5  # placeholder for engagement-based decisions

# Intent detection threshold (for interactive console)
INTENT_CONFIDENCE_THRESHOLD = 0.45


# Rate limiting and cycle settings for autonomous engagement:
ACTION_LIMIT_PER_HOUR = 15# Maximum number of like/comment actions per hour.
ENGAGEMENT_CYCLE_MIN = 600   # Minimum seconds between engagement cycles (e.g., 5 minutes)
ENGAGEMENT_CYCLE_MAX = 1200   # Maximum seconds between cycles (e.g., 10 minutes)

# Engagement thresholds:
POST_EXPOSURE_THRESHOLD = 200  # Minimum number of likes a post must have to be engaged with

# Commenting mode:
USE_ADVANCED_COMMENT = True  # Set to True to use advanced comment generation, False for simple comments.

# Advanced commenting rate limit:
ADVANCED_COMMENT_LIMIT_PER_HOUR = 1

# Global switch to enable/disable commenting
USE_COMMENTING = False

FULL_AUTONOMOUS_MODE = False

HUMAN_DELAY_PROFILES = {
        'default': {'min': 3, 'max': 8, 'alpha': 2, 'beta': 0.8},
        'post_like': {'min': 2.5, 'max': 9.5, 'alpha': 3, 'beta': 1.2},
        'comment': {'min': 4.0, 'max': 12.0, 'alpha': 2.5, 'beta': 1.5},
        'story_view': {'min': 1.8, 'max': 3.2, 'alpha': 2, 'beta': 0.7},
        'scroll': {'min': 0.5, 'max': 1.5, 'alpha': 1.5, 'beta': 0.4}
    }

SAFE_HOURLY_LIMITS = {
        'like': 18,
        'comment': 5,
        'advanced_comment': 2,
        'story_view': 15,
        'scroll': 8
    }