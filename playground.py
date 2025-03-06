

from src.utils.instagram_integration import InstagramIntegration

# Initialize the integration for Lia
bot = InstagramIntegration('lia')

if bot.login():
    # Replace with an actual post URL (or reuse the one from the comment test)
    post_url = "https://www.instagram.com/p/DG3hW_rMm5L/"
    media_id = bot.client.media_pk_from_url(post_url)
    like_result = bot.like_post(media_id)
    print("Like success:", like_result)
else:
    print("Login failed; cannot test like functionality.")
