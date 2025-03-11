import shlex
from src.utils.instagram_integration import InstagramIntegration

def handle_instagram_command(command_str: str, persona_name: str) -> str:
    """
    Handles explicit /instagram commands.
    Returns a result string.
    """
    try:
        args = shlex.split(command_str)
    except ValueError as e:
        return f"Error parsing command: {e}"
    
    if len(args) < 3:
        return "Usage: /instagram <action> <parameters>"
    
    action = args[1].strip().lower()
    ig_bot = InstagramIntegration(persona_name)
    if not ig_bot.login():
        return "Instagram login failed; please check your credentials."
    
    try:
        if action == "post":
            if len(args) < 4:
                return "Usage for post: /instagram post <image_url> <caption>"
            image_source = args[2]
            caption = " ".join(args[3:])
            result = ig_bot.post_content(image_source, caption)
            return f"Instagram post success: {result}"
        elif action == "comment":
            if len(args) < 4:
                return "Usage for comment: /instagram comment <post_url> <comment_text>"
            post_url = args[2]
            comment_text = " ".join(args[3:])
            media_id = ig_bot.client.media_pk_from_url(post_url)
            result = ig_bot.comment_on_post(media_id, comment_text)
            return f"Instagram comment success: {result}"
        elif action == "dm":
            if len(args) < 4:
                return "Usage for dm: /instagram dm <target_username> <message>"
            target_username = args[2]
            message = " ".join(args[3:])
            user_id = ig_bot.client.user_id_from_username(target_username)
            result = ig_bot.send_dm(user_id, message)
            return f"Instagram DM success: {result}"
        elif action == "like":
            if len(args) < 3:
                return "Usage for like: /instagram like <post_url>"
            post_url = args[2]
            media_id = ig_bot.client.media_pk_from_url(post_url)
            result = ig_bot.like_post(media_id)
            return f"Instagram like success: {result}"
        elif action == "follow":
            if len(args) < 3:
                return "Usage for follow: /instagram follow <target_username>"
            target_username = args[2]
            user_id = ig_bot.client.user_id_from_username(target_username)
            result = ig_bot.follow_user(user_id)
            return f"Instagram follow success: {result}"
        else:
            return "Unknown Instagram action. Supported actions: post, comment, dm, like, follow"
    except Exception as e:
        return f"Error handling Instagram command: {e}"
