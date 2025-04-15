"""
Working Instagram Bot - Reverted to Original Working Version
This is the version that was confirmed to be working correctly
"""

import os
import json
import random
import time
from datetime import datetime, timedelta
from math import exp
import logging

from src.utils.instagram_integration import InstagramIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('instagram_bot')

class SafetyLimiter:
    """Tracks and enforces safety limits for Instagram actions"""
    
    def __init__(self):
        self.counters = {
            'follow': 0,
            'scroll': 0,
            'profile_view': 0
        }
        self.reset_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.success_rates = {k: 1.0 for k in self.counters}
        self.last_actions = {}
        self.SAFE_HOURLY_LIMITS = {
            'follow': 12,
            'scroll': 30,
            'profile_view': 25
        }
        self.DAILY_FOLLOW_LIMIT = 50
        
        # Load state from file if exists
        self._load_state()

    def _load_state(self):
        """Load daily follow count from state file"""
        try:
            state_file = 'instagram_bot_state.json'
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    
                # Check if state is from today
                last_update = datetime.fromisoformat(state.get('last_update', '2000-01-01'))
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                if last_update >= today:
                    self.daily_follow_count = state.get('daily_follow_count', 0)
                    logger.info(f"Loaded daily follow count: {self.daily_follow_count}")
                else:
                    self.daily_follow_count = 0
                    logger.info("Reset daily follow count (new day)")
            else:
                self.daily_follow_count = 0
                logger.info("No state file found, starting with zero daily follows")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            self.daily_follow_count = 0

    def _save_state(self):
        """Save daily follow count to state file"""
        try:
            state = {
                'daily_follow_count': self.daily_follow_count,
                'last_update': datetime.now().isoformat()
            }
            with open('instagram_bot_state.json', 'w') as f:
                json.dump(state, f)
            logger.info(f"Saved state with {self.daily_follow_count} daily follows")
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def can_perform(self, action_type):
        """Check if an action can be performed within safety limits"""
        if action_type == 'follow':
            return (self.counters[action_type] < self.SAFE_HOURLY_LIMITS.get(action_type, 1) and
                    self.daily_follow_count < self.DAILY_FOLLOW_LIMIT)
        return self.counters[action_type] < self.SAFE_HOURLY_LIMITS.get(action_type, 1)

    def record(self, action_type, success=True):
        """Record an action and update counters"""
        self.counters[action_type] += 1
        if action_type == 'follow' and success:
            self.daily_follow_count += 1
            self._save_state()  # Save state after each successful follow
            
        self.last_actions[action_type] = datetime.now()
        self.success_rates[action_type] = 0.8 * self.success_rates[action_type] + 0.2 * float(success)

    def get_dynamic_delay(self, action_type):
        """Calculate a dynamic delay based on recent activity"""
        base_delay = random.uniform(1, 3)
        last_action = self.last_actions.get(action_type)
        if last_action:
            elapsed = (datetime.now() - last_action).total_seconds()
            if elapsed < base_delay:
                penalty = exp((base_delay - elapsed) / 7.5) - 1
                base_delay += penalty
        return base_delay * random.uniform(0.85, 1.15)

    def get_stats(self):
        """Get current statistics"""
        return {
            "hourly_stats": self.counters,
            "daily_follows": self.daily_follow_count,
            "daily_limit": self.DAILY_FOLLOW_LIMIT,
            "hourly_limits": self.SAFE_HOURLY_LIMITS
        }


class HumanBehaviorSimulator:
    """Simulates human-like behavior patterns"""
    
    @staticmethod
    def delay(action_type='default'):
        """Add a realistic delay for the specified action type"""
        profiles = {
            'default': {'min': 1.0, 'max': 4.0, 'alpha': 2.0, 'beta': 1.0},
            'profile_view': {'min': 2.0, 'max': 6.0, 'alpha': 2.5, 'beta': 1.2},
            'post_view': {'min': 2.0, 'max': 8.0, 'alpha': 3.0, 'beta': 1.5},
            'scroll': {'min': 1.0, 'max': 3.0, 'alpha': 1.8, 'beta': 0.8},
            'hesitation': {'min': 2.0, 'max': 5.0, 'alpha': 1.5, 'beta': 2.0}
        }
        
        profile = profiles.get(action_type, profiles['default'])
        base_delay = random.gammavariate(profile['alpha'], profile['beta'])
        clamped_delay = min(max(base_delay, profile['min']), profile['max'])
        
        # Add occasional slight variation
        if random.random() < 0.25:
            clamped_delay += random.uniform(0.1, 0.8)
            
        time.sleep(clamped_delay)
        return clamped_delay

    @staticmethod
    def should_hesitate():
        """Determine if hesitation should occur"""
        return random.random() < 0.15

    @staticmethod
    def should_abort_action():
        """Determine if an action should be aborted"""
        return random.random() < 0.05


def load_target_users():
    """Load target users from configuration"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "target_users.json")
        if not os.path.exists(config_path):
            logger.warning(f"File not found: {config_path}")
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "target_users.json")
            if not os.path.exists(config_path):
                logger.warning(f"Alternate path not found: {config_path}")
                
                # Fallback to config module if available
                try:
                    from src.config import TARGET_USERS
                    if TARGET_USERS:
                        logger.info(f"Using {len(TARGET_USERS)} target users from config module")
                        users = TARGET_USERS.copy()
                        random.shuffle(users)
                        return users
                except (ImportError, AttributeError):
                    logger.warning("No TARGET_USERS found in config module")
                return []
                
        with open(config_path) as f:
            users = json.load(f)
            random.shuffle(users)
            return users
    except Exception as e:
        logger.error(f"Target user error: {e}")
        return []


def ensure_valid_session(ig_bot):
    """Validate and ensure a working Instagram session"""
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Quick validation test - without amount parameter
            feed = ig_bot.client.get_timeline_feed()
            if feed:  # Check if response is valid
                logger.info("Session is valid")
                return True
        except Exception as e:
            error_msg = str(e).lower()
            attempt += 1
            
            if "user_has_logged_out" in error_msg or "login_required" in error_msg:
                logger.info(f"Session expired. Attempting relogin ({attempt}/{max_attempts})...")
                
                # Add a cooling period before attempting login again
                cooldown = 10 * attempt
                logger.info(f"Cooling down for {cooldown} seconds...")
                time.sleep(cooldown)
                
                # Remove session file to force fresh login
                if os.path.exists(ig_bot.session_file):
                    os.remove(ig_bot.session_file)
                    
                # Attempt login after delay
                time.sleep(random.uniform(2, 5))
                if ig_bot.login():
                    time.sleep(random.uniform(3, 7))  # Add post-login delay
                    continue
            else:
                logger.error(f"Unknown error validating session: {e}")
        
        if attempt < max_attempts:
            delay = random.uniform(20, 40) * attempt
            logger.info(f"Attempt {attempt} failed. Waiting {delay:.1f}s before next attempt...")
            time.sleep(delay)
    
    logger.error("Failed to establish valid session after multiple attempts")
    return False


def get_user_id_safely(ig_bot, username):
    """Get user ID with improved error handling and session validation"""
    max_retries = 3
    
    # First ensure we have a valid session
    if not ensure_valid_session(ig_bot):
        return None
        
    for attempt in range(max_retries):
        try:
            # Add small random delay before API call
            time.sleep(random.uniform(1, 3))
            
            # Use the private endpoint for better reliability
            user_info = ig_bot.client.user_info_by_username_v1(username)
            if user_info and hasattr(user_info, "pk"):
                return user_info.pk
        except Exception as e:
            error_message = str(e).lower()
            
            if "user_has_logged_out" in error_message or "login_required" in error_message:
                logger.info(f"Session issue during user lookup. Reconnecting... ({attempt+1}/{max_retries})")
                if not ensure_valid_session(ig_bot):
                    logger.error("Failed to re-establish session. Aborting.")
                    return None
            elif "not found" in error_message:
                logger.warning(f"User {username} not found.")
                return None
            else:
                logger.error(f"Error getting user ID for {username} (attempt {attempt+1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = (20 * (2 ** attempt)) * random.uniform(0.8, 1.2)
                logger.info(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to get user ID for {username} after {max_retries} attempts")
                return None
    
    return None


def simulate_organic_browse(ig_bot, limiter, duration_seconds=None):
    """
    Simulate organic browsing behavior for a specified duration
    
    Args:
        ig_bot: Instagram bot instance
        limiter: Safety limiter instance
        duration_seconds: Optional duration to browse for (in seconds)
    """
    if not limiter.can_perform('scroll'):
        return
        
    if not ensure_valid_session(ig_bot):
        logger.warning("Invalid session before browsing. Skipping.")
        return
    
    start_time = time.time()
    browse_count = 0
    
    try:
        logger.info("Simulating organic browsing...")
        
        # Continue browsing until duration is reached (if specified)
        while duration_seconds is None or (time.time() - start_time) < duration_seconds:
            # More varied browsing behavior
            browse_type = random.choice(['feed', 'explore', 'feed'])
            
            if browse_type == 'feed':
                logger.info("Browsing main feed...")
                try:
                    # Get timeline feed without amount parameter
                    feed = ig_bot.client.get_timeline_feed()
                    feed_items = feed.get('feed_items', [])
                    
                    view_count = random.randint(3, 8)  # More variable browsing depth
                    logger.info(f"Viewing {view_count} items from feed")
                    
                    # Limit to available items or view_count, whichever is smaller
                    actual_count = min(view_count, len(feed_items))
                    
                    for i in range(actual_count):
                        if not limiter.can_perform('scroll'):
                            logger.info("Reached scroll limit. Stopping browse.")
                            return
                            
                        HumanBehaviorSimulator.delay('scroll')
                        logger.info(f"Scrolling feed item {i+1}/{actual_count}")
                        limiter.record('scroll')
                        browse_count += 1
                        
                        # Add random pauses to simulate reading content
                        if random.random() < 0.4:
                            pause = random.uniform(2, 10)
                            logger.info(f"Pausing for {pause:.1f}s to view content")
                            time.sleep(pause)
                            
                        if HumanBehaviorSimulator.should_hesitate():
                            logger.info("Hesitating...")
                            HumanBehaviorSimulator.delay('hesitation')
                            
                        # Check if we've reached the duration
                        if duration_seconds and (time.time() - start_time) >= duration_seconds:
                            logger.info(f"Reached browsing duration of {duration_seconds}s")
                            return
                except Exception as e:
                    logger.error(f"Feed fetch error: {e}")
                    if "user_has_logged_out" in str(e).lower():
                        ensure_valid_session(ig_bot)
            
            elif browse_type == 'explore':
                logger.info("Browsing explore page...")
                try:
                    # Add explore page browsing simulation
                    for i in range(random.randint(3, 7)):
                        if not limiter.can_perform('scroll'):
                            logger.info("Reached scroll limit. Stopping browse.")
                            return
                            
                        HumanBehaviorSimulator.delay('scroll')
                        logger.info(f"Viewing explore content {i+1}")
                        limiter.record('scroll')
                        browse_count += 1
                        time.sleep(random.uniform(1, 8))
                        
                        # Check if we've reached the duration
                        if duration_seconds and (time.time() - start_time) >= duration_seconds:
                            logger.info(f"Reached browsing duration of {duration_seconds}s")
                            return
                except Exception as e:
                    logger.error(f"Explore browse error: {e}")
            
            # If duration specified and we've done at least 5 browse actions, 
            # randomly decide if we should stop early
            if duration_seconds and browse_count >= 5 and random.random() < 0.3:
                logger.info("Randomly ending browse session early")
                return
                
            # Add a pause between different browse types
            time.sleep(random.uniform(3, 8))
            
    except Exception as e:
        logger.error(f"Organic browse error: {e}")


def follow_from_user_followers(ig_bot, target_username, limiter, max_follows=3):
    """
    Follow users from a target user's follower list
    
    Args:
        ig_bot: Instagram bot instance
        target_username: Username of the target account
        limiter: Safety limiter instance
        max_follows: Maximum number of users to follow
        
    Returns:
        int: Number of users successfully followed
    """
    follows_count = 0
    try:
        # Pre-validation of session before starting
        if not ensure_valid_session(ig_bot):
            logger.warning("Invalid session before starting follower process. Taking a break.")
            return 0
            
        user_id = get_user_id_safely(ig_bot, target_username)
        if not user_id:
            logger.warning(f"Could not retrieve user ID for {target_username}. Skipping.")
            return 0

        if limiter.can_perform('profile_view'):
            logger.info(f"Viewing profile of {target_username}...")
            HumanBehaviorSimulator.delay('profile_view')
            try:
                # Use the private endpoint to view profile with extra error handling
                user_info = ig_bot.client.user_info_by_username_v1(target_username)
                limiter.record('profile_view')
                # Add a more natural delay after viewing profile
                time.sleep(random.uniform(2, 5))
            except Exception as e:
                logger.error(f"Error viewing profile: {e}")
                if "user_has_logged_out" in str(e).lower():
                    if not ensure_valid_session(ig_bot):
                        return 0
            
            if HumanBehaviorSimulator.should_hesitate():
                logger.info("Hesitating...")
                HumanBehaviorSimulator.delay('hesitation')

        try:
            logger.info(f"Fetching followers for {target_username}...")
            
            # Add delay before fetching followers
            time.sleep(random.uniform(3, 7))
            
            # Get followers with pagination and random delays
            amount = random.randint(30, 50)  # Increased to have more candidates
            followers = ig_bot.client.user_followers(user_id, amount=amount)
            
            if not followers:
                logger.warning(f"No followers found for {target_username}")
                return 0
                
            # Convert to list and shuffle for randomness
            follower_ids = list(followers.keys())
            random.shuffle(follower_ids)
            
            # Limit number of followers to process
            follower_ids = follower_ids[:min(len(follower_ids), 50)]
            
            follows_attempted = 0
            for follower_id in follower_ids:
                if follows_count >= max_follows:
                    logger.info(f"Reached maximum follows ({max_follows}). Stopping.")
                    break
                    
                if not limiter.can_perform('follow'):
                    logger.warning("Follow limit reached. Stopping.")
                    break
                    
                # Get follower info
                try:
                    follower_info = followers[follower_id]
                    follower_username = follower_info.username
                    
                    # Skip private accounts sometimes
                    if follower_info.is_private and random.random() < 0.7:
                        logger.info(f"Skipping private account: {follower_username}")
                        continue
                        
                    # Skip accounts with too many or too few followers
                    if hasattr(follower_info, 'follower_count'):
                        if follower_info.follower_count > 5000 or follower_info.follower_count < 10:
                            logger.info(f"Skipping account with {follower_info.follower_count} followers: {follower_username}")
                            continue
                            
                    # View follower profile (more human-like)
                    if limiter.can_perform('profile_view'):
                        logger.info(f"Viewing profile of potential follow: {follower_username}")
                        HumanBehaviorSimulator.delay('profile_view')
                        try:
                            ig_bot.client.user_info(follower_id)
                            limiter.record('profile_view')
                            # Variable delay after viewing profile
                            time.sleep(random.uniform(3, 8))
                        except Exception as e:
                            logger.error(f"Error viewing follower profile: {e}")
                            if "user_has_logged_out" in str(e).lower():
                                if not ensure_valid_session(ig_bot):
                                    return follows_count
                                    
                    # Sometimes browse posts before following
                    if limiter.can_perform('scroll') and random.random() < 0.7:
                        try:
                            # Get post count safely
                            media_count = 0
                            if hasattr(follower_info, 'media_count'):
                                media_count = follower_info.media_count
                            elif isinstance(follower_info, dict):
                                media_count = follower_info.get('media_count', 0)
                                
                            if media_count > 0:
                                # More natural browsing pattern
                                post_count = min(random.randint(1, 3), media_count)
                                logger.info(f"Browsing {post_count} posts from {follower_username}...")
                                
                                # Add delay before fetching media
                                time.sleep(random.uniform(2, 5))
                                
                                try:
                                    posts = ig_bot.client.user_medias(follower_id, amount=post_count)
                                    for post in posts:
                                        if random.random() < 0.8:  # Sometimes skip posts to appear more natural
                                            HumanBehaviorSimulator.delay('post_view')
                                            try:
                                                ig_bot.client.media_info(post.id)
                                                # Variable viewing time for posts
                                                time.sleep(random.uniform(2, 10))
                                            except Exception as e:
                                                logger.error(f"Error viewing post info: {e}")
                                                if "user_has_logged_out" in str(e).lower():
                                                    if not ensure_valid_session(ig_bot):
                                                        return follows_count
                                except Exception as e:
                                    logger.error(f"Error fetching posts for {follower_username}: {e}")
                            limiter.record('scroll')
                        except Exception as e:
                            logger.error(f"Error during post browsing: {e}")

                    # Occasionally "change mind" about following - more natural behavior
                    if HumanBehaviorSimulator.should_abort_action() or random.random() < 0.2:
                        logger.info(f"Changed mind about following {follower_username}")
                        continue

                    logger.info(f"Following {follower_username}...")
                    # Variable delay before follow action
                    wait_time = random.uniform(3, 8)
                    logger.info(f"Waiting {wait_time:.1f}s before follow action")
                    time.sleep(wait_time)
                    
                    try:
                        success = ig_bot.follow_user(follower_id)
                        if success:
                            follows_count += 1
                            limiter.record('follow', True)
                            logger.info(f"Successfully followed {follower_username}")
                            
                            # Longer cooldown after successful follow
                            cooldown = random.uniform(20, 40)
                            logger.info(f"Taking a {cooldown:.1f}s break before next action")
                            time.sleep(cooldown)
                            
                            # Add some browsing between follows for more natural behavior
                            if random.random() < 0.5 and limiter.can_perform('scroll'):
                                logger.info("Adding some browsing between follows")
                                simulate_organic_browse(ig_bot, limiter, duration_seconds=random.uniform(30, 60))
                        else:
                            limiter.record('follow', False)
                            logger.warning(f"Failed to follow {follower_username}")
                            # Add cooldown even after failure
                            time.sleep(random.uniform(10, 20))
                    except Exception as e:
                        logger.error(f"Error following user {follower_username}: {e}")
                        limiter.record('follow', False)
                        
                        # Check for session expiry
                        if "user_has_logged_out" in str(e).lower():
                            logger.warning("Session expired during follow attempt. Re-establishing...")
                            if not ensure_valid_session(ig_bot):
                                return follows_count
                    continue
                except Exception as e:
                    logger.error(f"Error processing follower {follower_id}: {e}")

        except Exception as e:
            logger.error(f"Error getting followers: {e}")
    except Exception as e:
        logger.error(f"Follow process error: {e}")
    
    return follows_count


def run_engagement_cycles(ig_bot, num_cycles=10):
    """
    Run multiple engagement cycles
    
    Args:
        ig_bot: Instagram bot instance
        num_cycles: Number of cycles to run
        
    Returns:
        dict: Results of the engagement cycles
    """
    # Initial login
    logger.info("Attempting Instagram login...")
    if not ig_bot.login():
        logger.error("Instagram login failed. Exiting.")
        return {"status": "error", "message": "Login failed"}
    
    logger.info("Instagram login successful.")
    
    limiter = SafetyLimiter()
    target_users = load_target_users()
    
    if not target_users:
        logger.error("No target users found. Please add users to target_users.json or config.py")
        return {"status": "error", "message": "No target users found"}
    
    total_follows = 0
    cycles_completed = 0
    
    for cycle in range(1, num_cycles + 1):
        logger.info(f"\n=== Starting Cycle #{cycle}/{num_cycles} ===")
        
        # Display current stats
        stats = limiter.get_stats()
        logger.info(f"Current stats: {json.dumps(stats, indent=2)}")
        
        # Check if we've already reached daily limit
        if limiter.daily_follow_count >= limiter.DAILY_FOLLOW_LIMIT:
            logger.warning(f"Daily follow limit ({limiter.DAILY_FOLLOW_LIMIT}) already reached. Stopping cycles.")
            break
        
        # Check session before starting cycle
        if not ensure_valid_session(ig_bot):
            logger.error("Unable to establish valid session. Stopping cycles.")
            break
            
        # Select a target user
        if not target_users:
            logger.warning("No more target users available. Stopping cycles.")
            break
            
        target_user = target_users.pop(0)
        logger.info(f"Selected target user: {target_user}")
        
        # Randomly choose behavior pattern
        if random.random() < 0.5:
            # Browse first, then follow
            logger.info("Simulating organic Browse...")
            simulate_organic_browse(ig_bot, limiter, duration_seconds=random.uniform(60, 180))
            
            # Check session again before following
            if ensure_valid_session(ig_bot):
                # Follow users
                follows = follow_from_user_followers(
                    ig_bot,
                    target_user,
                    limiter,
                    max_follows=random.randint(1, 3)
                )
                total_follows += follows
                
                # More browsing after following
                simulate_organic_browse(ig_bot, limiter, duration_seconds=random.uniform(30, 90))
        else:
            # Follow first, then browse
            # Check session before following
            if ensure_valid_session(ig_bot):
                # Follow users
                follows = follow_from_user_followers(
                    ig_bot,
                    target_user,
                    limiter,
                    max_follows=random.randint(1, 3)
                )
                total_follows += follows
                
                # Browse after following
                logger.info("Simulating organic Browse...")
                simulate_organic_browse(ig_bot, limiter, duration_seconds=random.uniform(60, 180))
        
        cycles_completed += 1
        
        # Take a long break between cycles
        if cycle < num_cycles:
            cooldown_minutes = random.uniform(8, 20)
            logger.info(f"Cycle complete. Cooling down for {cooldown_minutes:.1f} minutes")
            
            # Save state before long break
            logger.info("Saving state...")
            limiter._save_state()
            
            # Occasionally take an extra long break
            if random.random() < 0.2:
                cooldown_minutes = random.uniform(10, 30)
                logger.info(f"Taking an extra long break: {cooldown_minutes:.1f} minutes")
                
            # Convert to seconds
            cooldown_seconds = cooldown_minutes * 60
            
            # Sleep in smaller chunks to allow for interruption
            chunk_size = 30  # seconds
            chunks = int(cooldown_seconds / chunk_size)
            
            for i in range(chunks):
                time.sleep(chunk_size)
                # Check for interruption
                if i % 4 == 0:  # Every 2 minutes
                    logger.info(f"Cooling down... {(i+1)*chunk_size/60:.1f}/{cooldown_minutes:.1f} minutes elapsed")
    
    # Final stats
    final_stats = limiter.get_stats()
    logger.info(f"Final stats: {json.dumps(final_stats, indent=2)}")
    
    return {
        "status": "success",
        "cycles_completed": cycles_completed,
        "total_follows": total_follows,
        "daily_follows": limiter.daily_follow_count
    }


def main():
    """Main entry point"""
    try:
        # Import persona if available, otherwise use default
        try:
            from src.utils.openai_integration import LiaLama
            persona = LiaLama("src/profiles/lia_lama.json")
            ig_bot = InstagramIntegration(persona.profile.name.split()[0].lower())
            logger.info(f"Using persona: {persona.profile.name}")
        except (ImportError, FileNotFoundError):
            # Fallback to default
            ig_bot = InstagramIntegration("instagram_bot")
            logger.info("Using default bot name")
        
        # Run engagement cycles
        result = run_engagement_cycles(ig_bot)
        logger.info(f"Engagement result: {json.dumps(result, indent=2)}")
        return result
        
    except KeyboardInterrupt:
        logger.info("\nProgram interrupted by user")
        return {"status": "interrupted", "message": "Program interrupted by user"}
    except Exception as e:
        logger.error(f"Critical error: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    main()
