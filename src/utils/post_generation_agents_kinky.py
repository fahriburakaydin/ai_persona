import json

def compute_context_intensity(conversation_context: str) -> float:
    """
    Computes a score (0 to 1) indicating how strongly the conversation signals a post.
    Uses a simple heuristic: counts keywords like 'post', 'share', 'now', 'urgent', and 'trending'.
    """
    keywords = ["post", "share", "now", "urgent", "trending"]
    count = sum(conversation_context.lower().count(kw) for kw in keywords)
    intensity = min(count / 10, 1.0)
    return intensity

def generate_weighted_post_plan_kinky(persona, conversation_context: str, intensity_threshold: float = 0.5) -> dict:
    f"""
    Generates a creative post kinky plan based on conversation context and Lia's personality.
    The output is a JSON object with keys:
      - "image_idea": a creative description for the image.
      - "caption": an engaging caption.
      - "post_category": "self" if the post should feature Lia, or "general" otherwise.
      
    If the conversation context is strong (intensity >= threshold), it uses it;
    otherwise, it defaults to a baseline prompt reflecting {persona}'s stable personality.
    """
    personality_details = f"Traits: {', '.join(persona.profile.personality_traits)}. Background: {persona.profile.background_story}"
    intensity = compute_context_intensity(conversation_context)
    
    
    print("🤖 Lia (Manager): No high impact input in recent conversations...Using personality for post planning.")
    prompt = (
        f"Personality: {personality_details}\n"
        "Generate a JSON object with keys 'image_idea', 'caption', and 'post_category'. "
        "This is a post for a KINKY account. So make sure to use the right tone and style."
        "The image should be seductive, revealing and erotic, and the caption should be engaging and inviting."
        "The 'image_idea' should be a creative description for an image.IT MAY BE NSFW."
        "the 'caption' should be engaging. NO HASHTAGS"
        "The image should feature a very attractive FEMALE PERSON 'post_category' should be 'self', nothing else."
        "POST CATEGORY may ONLY BE 'SELF'. Nothing else is allowed!"
    )
    
    response = persona.generate_response(prompt)
    try:
        plan = json.loads(response)
    except Exception as e:
        plan = {
            "image_idea": "a creative themed image reflecting your unique style",
            "caption": "An engaging caption that fits your personality.",
            "post_category": "self"
        }
    return plan
