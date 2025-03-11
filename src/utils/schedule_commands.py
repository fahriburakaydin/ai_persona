import shlex
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from src.utils.instagram_integration import InstagramIntegration

# Initialize a background scheduler (this module maintains its own scheduler instance)
scheduler = BackgroundScheduler()
scheduler.start()

def schedule_post_job(time_str: str, frequency: str, image_source: str, caption: str, persona_name: str) -> str:
    """
    Schedules a post job using provided parameters.
    Returns a confirmation message.
    """
    try:
        hour, minute = map(int, time_str.split(":"))
    except Exception as e:
        return "Invalid time format. Please use HH:MM (e.g., '10:00')."

    def scheduled_post():
        ig_bot = InstagramIntegration(persona_name)
        if ig_bot.login():
            import os
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
        return f"Scheduled daily post at {time_str}. (Job ID: {job.id})"
    elif frequency.lower() == "once":
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled_time < now:
            scheduled_time += timedelta(days=1)
        job = scheduler.add_job(scheduled_post, 'date', run_date=scheduled_time)
        return f"Scheduled one-time post at {scheduled_time} (Job ID: {job.id})."
    else:
        return "Unsupported frequency. Use 'daily' or 'once'."

def list_scheduled_jobs() -> str:
    jobs = scheduler.get_jobs()
    if not jobs:
        return "No scheduled jobs."
    output = "Scheduled Jobs:\n"
    for job in jobs:
        output += f"  Job ID: {job.id} | Next Run: {job.next_run_time} | Function: {job.func.__name__}\n"
    return output

def cancel_scheduled_job(job_id: str) -> str:
    try:
        scheduler.remove_job(job_id)
        return f"Cancelled job with ID: {job_id}"
    except Exception as e:
        return f"Failed to cancel job with ID {job_id}: {e}"
