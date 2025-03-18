import os
import json
import random
import time
from datetime import datetime, timedelta
from src.utils.instagram_integration import InstagramIntegration
from src.config import ACTION_LIMIT_PER_HOUR, ENGAGEMENT_CYCLE_MIN, ENGAGEMENT_CYCLE_MAX, POST_EXPOSURE_THRESHOLD, USE_ADVANCED_COMMENT, ADVANCED_COMMENT_LIMIT_PER_HOUR

# Function to load curated hashtags from a JSON file.
def load_curated_hashtags() -> list:
    config_path = os.path.join(os.getcwd(), "src", "config", "hashtags.json")
    try:
        with open(config_path, "r") as f:
            hashtags = json.load(f)
        return hashtags
    except Exception as e:
        print("Error loading hashtags:", e)
        return ["#inspiration", "#fashion", "#travel", "#coffee"]

# Global rate limiter for general actions.
current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
action_count = 0

def reset_rate_limiter():
    global current_hour, action_count
    now = datetime.now()
    if now >= current_hour + timedelta(hours=1):
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        action_count = 0

def can_take_action() -> bool:
    reset_rate_limiter()
    return action_count < ACTION_LIMIT_PER_HOUR

def record_action():
    global action_count
    action_count += 1

def human_delay(min_sec=1, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def fetch_candidate_posts(ig_bot, hashtag: str, limit: int = 10) -> list:
    # Remove any leading '#' if present.
    hashtag = hashtag.lstrip("#")
    try:
        posts = ig_bot.client.hashtag_medias_recent(hashtag, amount=limit)
        return posts
    except Exception as e:
        print("Failed to fetch posts for hashtag", hashtag, ":", e)
        return []


# Simple commenting using a more generic set of phrases.
def simple_comment(ig_bot, media_id: str) -> bool:
    if random.random() < 0.2:
        generic_comments = [
            "cool!:)",
            "Really nice!",
            "Love this!",
            "Awesome!",
            "😊👍",
            "✨✨",
            "👏😊",
            "💯💯",
            "😍😍"
        ]
        comment = random.choice(generic_comments)
        human_delay()
        return ig_bot.comment_on_post(media_id, comment)
    return False

# --- Advanced Comment Rate Limiting Setup ---
current_hour_adv = datetime.now().replace(minute=0, second=0, microsecond=0)
advanced_comment_count = 0

def reset_advanced_comment_rate():
    global current_hour_adv, advanced_comment_count
    now = datetime.now()
    if now >= current_hour_adv + timedelta(hours=1):
        current_hour_adv = now.replace(minute=0, second=0, microsecond=0)
        advanced_comment_count = 0

def can_advanced_comment() -> bool:
    reset_advanced_comment_rate()
    return advanced_comment_count < ADVANCED_COMMENT_LIMIT_PER_HOUR

def record_advanced_comment():
    global advanced_comment_count
    advanced_comment_count += 1

# Advanced commenting that uses Lia's language model to generate a tailored comment.
def advanced_comment(ig_bot, media_id: str, post_caption: str, persona) -> bool:
    if not can_advanced_comment():
        print("Advanced comment limit reached for this hour. Falling back to simple comment.")
        return simple_comment(ig_bot, media_id)
    
    # Generate a prompt for advanced comment generation using Lia's tone and style.
    prompt = (
        "You are Lia, a witty, sarcastic, and insightful social media influencer known for your distinctive tone. "
        "Based on the following Instagram caption, generate a brief, relevant, and engaging comment that reflects your natural communication style: "
        f"'{post_caption}'."
    )
    comment = persona.generate_response(prompt).strip()
    if comment:
        human_delay()
        success = ig_bot.comment_on_post(media_id, comment)
        if success:
            record_advanced_comment()
        return success
    return False

def autonomous_engage(ig_bot, persona):
    hashtags = load_curated_hashtags()
    chosen_hashtag = random.choice(hashtags)
    print(f"Using curated hashtag: {chosen_hashtag}")
    
    posts = fetch_candidate_posts(ig_bot, chosen_hashtag)
    print(f"Found {len(posts)} candidate posts under {chosen_hashtag}.")
    
    for post in posts:
        media_id = str(post.pk)
        post_url = f"https://www.instagram.com/p/{post.code}/" if hasattr(post, "code") else "URL not available"

        # Check exposure: only engage with posts having sufficient likes.
        if hasattr(post, 'like_count') and post.like_count < POST_EXPOSURE_THRESHOLD:
            print(f"Skipping post {media_id} due to low exposure ({post.like_count} likes).")
            continue
        
        if can_take_action():
            if random.random() < 0.7:
                if ig_bot.like_post(media_id):
                    record_action()
                    print(f"Liked post {media_id} ({post_url}).")            if can_take_action():
                if USE_ADVANCED_COMMENT:
                    if advanced_comment(ig_bot, media_id, getattr(post, "caption_text", ""), persona):
                        record_action()
                        print(f"Advanced commented on post {media_id} ({post_url}).")
                else:
                    if simple_comment(ig_bot, media_id):
                        record_action()
                        print(f"Commented on post {media_id} ({post_url}).")
            time.sleep(random.uniform(2, 5))

def run_autonomous_engagement():
    ig_bot = InstagramIntegration("lia")
    if not ig_bot.login():
        print("Instagram login failed; cannot engage.")
        return

    while True:
        print("\nScanning for posts to engage with...")
        autonomous_engage(ig_bot, persona)
        print("Engagement cycle complete. Waiting before next cycle...")
        time.sleep(random.uniform(ENGAGEMENT_CYCLE_MIN, ENGAGEMENT_CYCLE_MAX))

if __name__ == "__main__":
    from src.utils.openai_integration import LiaLama
    persona = LiaLama("src/profiles/lia_lama.json", debug=True)
    run_autonomous_engagement()
