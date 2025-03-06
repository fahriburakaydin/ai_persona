import shlex
from src.utils.openai_integration import LiaLama
from src.utils.instagram_integration import InstagramIntegration

# Load the persona's profile (e.g., Lia's JSON)
persona = LiaLama("src/profiles/lia_lama.json", debug=True)

# Extract only the first name for display and internal use
first_name = persona.profile.name.split()[0]
persona_name = first_name.lower()  # used internally (e.g., for session file naming)
display_name = first_name         # used for UI display messages


def interactive_chat():
    """
    Starts an interactive console to chat with {display_name}, observe learning,
    and provide real-time feedback.
    """
    print(f"\n🌀 Welcome to {display_name}'s Console! You can chat, observe learning, and give feedback. Type 'exit' to quit.\n")

    while True:
        user_input = input("🗨️ You: ")

        # Check if the command is for Instagram actions
        if user_input.startswith("/instagram"):
            try:
                # Use shlex.split to properly handle quoted strings
                args = shlex.split(user_input)
            except ValueError as e:
                print("Error parsing command:", e)
                continue

            if len(args) < 3:
                print("Usage: /instagram <action> <parameters>")
                continue

            action = args[1].strip().lower()

            # Instantiate the Instagram integration using the dynamic persona name
            ig_bot = InstagramIntegration(persona_name)
            if not ig_bot.login():
                print("Instagram login failed; please check your credentials.")
                continue

            if action == "post":
                # Expected format: /instagram post <image_url> <caption>
                if len(args) < 4:
                    print("Usage for post: /instagram post <image_url> <caption>")
                else:
                    image_url = args[2]
                    caption = " ".join(args[3:])
                    result = ig_bot.post_content(image_url, caption)
                    print("Instagram post success:", result)
            elif action == "comment":
                # Expected format: /instagram comment <post_url> <comment_text>
                if len(args) < 4:
                    print("Usage for comment: /instagram comment <post_url> <comment_text>")
                else:
                    post_url = args[2]
                    comment_text = " ".join(args[3:])
                    media_id = ig_bot.client.media_pk_from_url(post_url)
                    result = ig_bot.comment_on_post(media_id, comment_text)
                    print("Instagram comment success:", result)
            elif action == "dm":
                # Expected format: /instagram dm <target_username> <message>
                if len(args) < 4:
                    print("Usage for dm: /instagram dm <target_username> <message>")
                else:
                    target_username = args[2]
                    message = " ".join(args[3:])
                    user_id = ig_bot.client.user_id_from_username(target_username)
                    result = ig_bot.send_dm(user_id, message)
                    print("Instagram DM success:", result)
            elif action == "like":
                # Expected format: /instagram like <post_url>
                post_url = args[2]
                media_id = ig_bot.client.media_pk_from_url(post_url)
                result = ig_bot.like_post(media_id)
                print("Instagram like success:", result)
            elif action == "follow":
                # Expected format: /instagram follow <target_username>
                if len(args) < 3:
                    print("Usage for follow: /instagram follow <target_username>")
                else:
                    target_username = args[2]
                    user_id = ig_bot.client.user_id_from_username(target_username)
                    result = ig_bot.follow_user(user_id)
                    print("Instagram follow success:", result)
            else:
                print("Unknown Instagram action. Supported actions: post, comment, dm, like, follow")
 
