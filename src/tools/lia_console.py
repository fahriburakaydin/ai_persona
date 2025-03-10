import os
import shlex
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from src.utils.openai_integration import LiaLama
from src.utils.instagram_integration import InstagramIntegration
from src.utils.intent_detector import detect_intent  # Advanced intent detector using zero-shot

# Load the persona's profile (e.g., Lia's JSON)
persona = LiaLama("src/profiles/lia_lama.json", debug=True)

# Extract only the first name for display and internal use (e.g., "Lia")
first_name = persona.profile.name.split()[0]
persona_name = first_name.lower()  # used internally (e.g., session file naming)
display_name = first_name         # used for UI display messages

# ---- Scheduler Integration ----

scheduler = BackgroundScheduler()
scheduler.start()
print("[Scheduler] BackgroundScheduler started.")

def schedule_post_job(time_str, frequency, image_source, caption):
    """
    Schedules a post job based on the provided time, frequency, image source (URL or local file path), and caption.
    """
    try:
        hour, minute = map(int, time_str.split(":"))
    except Exception as e:
        print("Invalid time format. Please use HH:MM (e.g., '10:00').")
        return

    def scheduled_post():
        ig_bot = InstagramIntegration(persona_name)
        if ig_bot.login():
            if os.path.exists(image_source):
                try:
                    result = ig_bot.client.photo_upload(
                        path=image_source,
                        caption=caption,
                        extra_data={"disable_comments": False}
                    )
                    print(f"[Scheduler] Scheduled post success: {result}")
                except Exception as e:
                    print(f"[Scheduler] Failed to post local image: {e}")
            else:
                try:
                    result = ig_bot.post_content(image_source, caption)
                    print(f"[Scheduler] Scheduled post success: {result}")
                except Exception as e:
                    print(f"[Scheduler] Failed to post image from URL: {e}")
        else:
            print("[Scheduler] Instagram login failed; scheduled post not executed.")

    if frequency.lower() == "daily":
        job = scheduler.add_job(scheduled_post, 'cron', hour=hour, minute=minute)
        print(f"[Scheduler] Scheduled daily post at {time_str}. (Job ID: {job.id})")
    elif frequency.lower() == "once":
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled_time < now:
            scheduled_time += timedelta(days=1)
        job = scheduler.add_job(scheduled_post, 'date', run_date=scheduled_time)
        print(f"[Scheduler] Scheduled one-time post at {scheduled_time} (Job ID: {job.id}).")
    else:
        print("Unsupported frequency. Use 'daily' or 'once'.")

def list_scheduled_jobs():
    """
    Lists all scheduled jobs with their IDs, next run times, and job function names.
    """
    jobs = scheduler.get_jobs()
    if not jobs:
        print("[Scheduler] No scheduled jobs.")
        return
    print("[Scheduler] Scheduled Jobs:")
    for job in jobs:
        print(f"  Job ID: {job.id} | Next Run: {job.next_run_time} | Function: {job.func.__name__}")

def cancel_scheduled_job(job_id):
    """
    Cancels a scheduled job based on its job ID.
    """
    try:
        scheduler.remove_job(job_id)
        print(f"[Scheduler] Cancelled job with ID: {job_id}")
    except Exception as e:
        print(f"[Scheduler] Failed to cancel job with ID {job_id}: {e}")

# ---- Interactive Chat Loop ----

def interactive_chat():
    """
    Starts an interactive console to chat with {display_name}, observe learning,
    and provide real-time feedback.
    """
    print(f"\n🌀 Welcome to {display_name}'s Console! You can chat, observe learning, and give feedback. Type 'exit' to quit.\n")

    while True:
        user_input = input("🗨️ You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"\n👋 Exiting {display_name}'s Console. See you next time!\n")
            break

        # Explicit slash commands take priority.
        if user_input.startswith("/"):
            # /schedule commands
            if user_input.startswith("/schedule"):
                try:
                    args = shlex.split(user_input)
                except ValueError as e:
                    print("Error parsing command:", e)
                    continue

                if len(args) < 2:
                    print("Usage: /schedule <command> [parameters]")
                    continue

                subcommand = args[1].strip().lower()
                if subcommand == "post":
                    # Expected: /schedule post <time> <frequency> <image_url> <caption>
                    if len(args) < 6:
                        print("Usage for scheduling post: /schedule post <time(HH:MM)> <frequency(daily|once)> <image_url> <caption>")
                        continue
                    time_str = args[2]
                    frequency = args[3]
                    image_source = args[4]
                    caption = " ".join(args[5:])
                    schedule_post_job(time_str, frequency, image_source, caption)
                elif subcommand == "list":
                    list_scheduled_jobs()
                elif subcommand == "cancel":
                    if len(args) < 3:
                        print("Usage for cancelling: /schedule cancel <job_id>")
                        continue
                    job_id = args[2]
                    cancel_scheduled_job(job_id)
                else:
                    print("Unknown schedule command. Supported commands: post, list, cancel")
                continue

            # /instagram commands
            if user_input.startswith("/instagram"):
                try:
                    args = shlex.split(user_input)
                except ValueError as e:
                    print("Error parsing command:", e)
                    continue

                if len(args) < 3:
                    print("Usage: /instagram <action> <parameters>")
                    continue

                action = args[1].strip().lower()
                ig_bot = InstagramIntegration(persona_name)
                if not ig_bot.login():
                    print("Instagram login failed; please check your credentials.")
                    continue

                if action == "post":
                    if len(args) < 4:
                        print("Usage for post: /instagram post <image_url> <caption>")
                    else:
                        image_source = args[2]
                        caption = " ".join(args[3:])
                        try:
                            result = ig_bot.post_content(image_source, caption)
                            print("Instagram post success:", result)
                        except Exception as e:
                            print("Error posting:", e)
                elif action == "comment":
                    if len(args) < 4:
                        print("Usage for comment: /instagram comment <post_url> <comment_text>")
                    else:
                        post_url = args[2]
                        comment_text = " ".join(args[3:])
                        media_id = ig_bot.client.media_pk_from_url(post_url)
                        result = ig_bot.comment_on_post(media_id, comment_text)
                        print("Instagram comment success:", result)
                elif action == "dm":
                    if len(args) < 4:
                        print("Usage for dm: /instagram dm <target_username> <message>")
                    else:
                        target_username = args[2]
                        message = " ".join(args[3:])
                        user_id = ig_bot.client.user_id_from_username(target_username)
                        result = ig_bot.send_dm(user_id, message)
                        print("Instagram DM success:", result)
                elif action == "like":
                    post_url = args[2]
                    media_id = ig_bot.client.media_pk_from_url(post_url)
                    result = ig_bot.like_post(media_id)
                    print("Instagram like success:", result)
                elif action == "follow":
                    if len(args) < 3:
                        print("Usage for follow: /instagram follow <target_username>")
                    else:
                        target_username = args[2]
                        user_id = ig_bot.client.user_id_from_username(target_username)
                        result = ig_bot.follow_user(user_id)
                        print("Instagram follow success:", result)
                else:
                    print("Unknown Instagram action. Supported actions: post, comment, dm, like, follow")
                continue

            # New /generate post command for interactive post creation
            if user_input.startswith("/generate post"):
                from src.utils.post_creator import interactive_post_creation
                interactive_post_creation(persona_name, display_name)
                continue

        # For inputs not starting with "/", use intent detection.
        intent_info = detect_intent(user_input)
        detected_intent = intent_info["intent"]
        confidence = intent_info.get("score", 0)
        print(f"Detected intent: {detected_intent}, Confidence score: {confidence:.3f}")

        # If a non-chat intent is detected with confidence above threshold, ask for confirmation.
        if detected_intent != "chat" and confidence >= 0.45:
            confirmation = input(f"Did you mean to trigger '{detected_intent}' action? (yes/no): ").strip().lower()
            if confirmation in ["yes", "y"]:
                if detected_intent == "post":
                    print("🤖 (Lia detects that you might want to post something.)")
                elif detected_intent == "comment":
                    print("🤖 (Lia detects that you might want to comment on a post.)")
                elif detected_intent == "follow":
                    print("🤖 (Lia detects that you might want to follow someone.)")
                elif detected_intent == "dm":
                    print("🤖 (Lia detects that you might want to send a DM.)")
                elif detected_intent == "schedule":
                    print("🤖 (Lia detects that you might want to schedule an action.)")
            else:
                detected_intent = "chat"

        # For chat or if no autonomous action is confirmed, generate a chat response.
        if detected_intent == "chat":
            response = persona.generate_response(user_input)
            print(f"\n💬 {display_name}: {response}\n")

      

if __name__ == "__main__":
    interactive_chat()
