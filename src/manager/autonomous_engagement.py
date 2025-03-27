import os
import json
import random
import time
import sys
from datetime import datetime, timedelta
from math import exp
from functools import wraps
from src.utils.instagram_integration import InstagramIntegration
from src.config import (
    ACTION_LIMIT_PER_HOUR, ENGAGEMENT_CYCLE_MIN, ENGAGEMENT_CYCLE_MAX,
    POST_EXPOSURE_THRESHOLD, USE_ADVANCED_COMMENT, ADVANCED_COMMENT_LIMIT_PER_HOUR,
    SAFE_HOURLY_LIMITS, HUMAN_DELAY_PROFILES, USE_COMMENTING
)

# Global simple comments definition
SIMPLE_COMMENTS = ["Nice!", "Cool 😊", "Love this!", "Awesome 👏", "Great shot!"]

# ======================
# SAFETY CORE COMPONENTS
# ======================

class SafetyLimiter:
    def __init__(self):
        self.counters = {
            'like': 0,
            'comment': 0,
            'advanced_comment': 0,
            'story_view': 0,
            'scroll': 0
        }
        self.reset_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.success_rates = {k: 1.0 for k in self.counters}
        self.last_actions = {}

    def _reset_counters(self):
        now = datetime.now()
        if now >= self.reset_time + timedelta(hours=1):
            self.counters = {k: 0 for k in self.counters}
            self.reset_time = now.replace(minute=0, second=0, microsecond=0)
            print("Hourly counters reset")

    def can_perform(self, action_type):
        self._reset_counters()
        return self.counters[action_type] < SAFE_HOURLY_LIMITS.get(action_type, 1)

    def record(self, action_type, success=True):
        self.counters[action_type] += 1
        self.last_actions[action_type] = datetime.now()
        # Update success rate with exponential decay
        self.success_rates[action_type] = 0.8 * self.success_rates[action_type] + 0.2 * float(success)
    
    def get_dynamic_delay(self, action_type):
        base_delay = random.uniform(1, 3)
        last_action = self.last_actions.get(action_type)
        if last_action:
            elapsed = (datetime.now() - last_action).total_seconds()
            if elapsed < base_delay:
                penalty = exp((base_delay - elapsed) / 7.5) - 1
                base_delay += penalty
        return base_delay * random.uniform(0.85, 1.15)

class HumanBehaviorSimulator:
    @staticmethod
    def delay(action_type='default'):
        profile = HUMAN_DELAY_PROFILES.get(action_type, HUMAN_DELAY_PROFILES['default'])
        base_delay = random.gammavariate(profile['alpha'], profile['beta'])
        clamped_delay = min(max(base_delay, profile['min']), profile['max'])
        if random.random() < 0.25:
            clamped_delay += random.uniform(0.1, 0.8)
        time.sleep(clamped_delay)
        return clamped_delay

    @staticmethod
    def should_hesitate():
        return random.random() < 0.15

# ======================
# CORE FUNCTIONALITY
# ======================

def load_hashtags():
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "hashtags.json")
        with open(config_path) as f:
            hashtags = json.load(f)
            # Rotate 30% of hashtags
            keep = int(len(hashtags) * 0.7)
            return hashtags[:keep] + random.sample(hashtags, len(hashtags) - keep)
    except Exception as e:
        print(f"Hashtag error: {e}")
        return random.sample(["#art", "#travel", "#food", "#fitness"], 4)

def fetch_posts(ig_bot, hashtag):
    try:
        amount = random.randint(8, 12)
        posts = ig_bot.client.hashtag_medias_recent(hashtag.lstrip("#"), amount=amount)
        return [p for p in posts if getattr(p, 'like_count', 0) >= POST_EXPOSURE_THRESHOLD][:8]
    except Exception as e:
        print(f"Post fetch error: {e}")
        return []

# ======================
# ORGANIC BEHAVIOR MODULES
# ======================

def simulate_feed_scroll(ig_bot, limiter):
    if not limiter.can_perform('scroll'):
        return
    try:
        print("Simulating feed scroll...")
        feed = ig_bot.client.get_timeline_feed().get('feed_items', [])
        random.shuffle(feed)
        for post in feed[:random.randint(3, 7)]:
            if HumanBehaviorSimulator.should_hesitate():
                HumanBehaviorSimulator.delay('scroll_hesitate')
                continue
            HumanBehaviorSimulator.delay('post_view')
            if limiter.can_perform('like') and random.random() < 0.12:
                if ig_bot.like_post(post['id']):
                    limiter.record('like')
                    print(f"Liked organic post {post['id'][:8]}...")
                    HumanBehaviorSimulator.delay('post_like')
        limiter.record('scroll')
    except Exception as e:
        print(f"Feed scroll error: {e}")

def handle_stories(ig_bot, limiter):
    if random.random() < 0.45 and limiter.can_perform('story_view'):
        try:
            stories = ig_bot.client.get_reels_tray().get('tray', [])
            random.shuffle(stories)
            for story in stories[:random.randint(1, 3)]:
                print(f"Viewing {story['user']['username']}'s story")
                ig_bot.client.seen_reels([{'id': story['id']}])
                limiter.record('story_view')
                if random.random() < 0.08:
                    reactions = ["❤️", "😍", "🔥", "👏"]
                    ig_bot.client.send_reaction(story['id'], random.choice(reactions))
                    HumanBehaviorSimulator.delay('story_react')
                HumanBehaviorSimulator.delay('story_view')
        except Exception as e:
            print(f"Story error: {e}")

def check_notifications(ig_bot, limiter):
    print("Checking notifications... (not implemented)")

def handle_hashtag_engagement(ig_bot, persona, limiter):
    hashtags = load_hashtags()
    chosen_hashtag = random.choice(hashtags)
    print(f"Engaging with posts under #{chosen_hashtag}")
    posts = fetch_posts(ig_bot, chosen_hashtag)
    for post in posts:
        media_id = str(post.pk)
        post_url = f"https://www.instagram.com/p/{post.code}/" if hasattr(post, "code") else "URL not available"
        actions = []
        if limiter.can_perform('like'):
            delay = limiter.get_dynamic_delay('like')
            HumanBehaviorSimulator.delay('like')
            try:
                if ig_bot.like_post(media_id):
                    limiter.record('like')
                    actions.append(f"Liked {media_id} ({post_url})")
            except Exception as e:
                print(f"Like error: {e}")
        # Commenting is switched off (USE_COMMENTING == False)
        if USE_COMMENTING and limiter.can_perform('comment'):
            try:
                # Advanced comment is attempted if possible; otherwise, simple comment.
                if limiter.can_perform('advanced_comment'):
                    success = perform_comment(ig_bot, media_id, getattr(post, "caption_text", ""), persona, limiter)
                    comment_type = "Advanced"
                else:
                    success = perform_comment(ig_bot, media_id, getattr(post, "caption_text", ""), persona, limiter)
                    comment_type = "Basic"
                if success:
                    actions.append(f"Commented ({comment_type}) on {media_id} ({post_url})")
            except Exception as e:
                print(f"Comment error: {e}")
        if actions:
            print(" | ".join(actions))
        time.sleep(random.uniform(2, 5))

# ======================
# ENGAGEMENT CORE
# ======================

def perform_comment(ig_bot, media_id, caption, persona, limiter):
    if HumanBehaviorSimulator.should_hesitate():
        print("Hesitation triggered - skipping comment")
        return False
    try:
        if limiter.can_perform('advanced_comment'):
            truncated = (caption[:95] + '...') if len(caption) > 100 else caption
            prompt = f"As Lia, create short witty comment (<6 words) for: '{truncated}'"
            comment = persona.generate_response(prompt).strip()
            if not (2 < len(comment) <= 35):
                comment = random.choice(SIMPLE_COMMENTS)
                action_type = 'comment'
            else:
                action_type = 'advanced_comment'
        else:
            comment = random.choice(SIMPLE_COMMENTS)
            action_type = 'comment'
        HumanBehaviorSimulator.delay('pre_comment')
        success = ig_bot.comment_on_post(media_id, comment)
        limiter.record(action_type, success)
        print(f"Generated comment: {comment}")
        return success
    except Exception as e:
        print(f"Comment error: {e}")
        return False

def engagement_cycle(ig_bot, persona, limiter):
    activities = [
        ('hashtag_engage', 0.7),
        ('feed_scroll', 0.6),
        ('stories', 0.45),
        ('notifications', 0.3)
    ]
    random.shuffle(activities)
    for activity, prob in activities:
        if random.random() < prob:
            if activity == 'hashtag_engage':
                handle_hashtag_engagement(ig_bot, persona, limiter)
            elif activity == 'feed_scroll':
                simulate_feed_scroll(ig_bot, limiter)
            elif activity == 'stories':
                handle_stories(ig_bot, limiter)
            elif activity == 'notifications':
                check_notifications(ig_bot, limiter)

# ======================
# MAIN CONTROLLER
# ======================

def run_safe_engagement(persona, ig_bot):
    if not ig_bot.login():
        print("Instagram login failed")
        return
    limiter = SafetyLimiter()
    try:
        while True:
            print("\n=== New Engagement Cycle ===")
            engagement_cycle(ig_bot, persona, limiter)
            base_cooldown = random.uniform(ENGAGEMENT_CYCLE_MIN, ENGAGEMENT_CYCLE_MAX)
            jittered = base_cooldown * random.uniform(0.8, 1.3)
            print(f"Cycle complete. Cooling down for {jittered/60:.1f} minutes")
            time.sleep(jittered)
    except Exception as e:
        print(f"Critical error: {e}")
        handle_error_shutdown(ig_bot)
        
def handle_error_shutdown(ig_bot):
    print("Critical error encountered. Initiating shutdown...")
    ig_bot.logout()
    sys.exit(1)

if __name__ == "__main__":
    from src.utils.openai_integration import LiaLama
    persona = LiaLama("src/profiles/lia_lama.json")
    ig_bot = InstagramIntegration(persona.profile.name.split()[0].lower())
    run_safe_engagement(persona)
