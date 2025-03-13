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

def generate_weighted_post_plan(persona, conversation_context: str, intensity_threshold: float = 0.5) -> dict:
    """
    Generates a creative post plan based on conversation context and Lia's personality.
    The output is a JSON object with keys:
      - "image_idea": a creative description for the image.
      - "caption": an engaging caption.
      - "post_category": "self" if the post should feature Lia, or "general" otherwise.
      
    If the conversation context is strong (intensity >= threshold), it uses it;
    otherwise, it defaults to a baseline prompt reflecting Lia’s stable personality.
    """
    personality_details = f"Traits: {', '.join(persona.profile.personality_traits)}. Background: {persona.profile.background_story}"
    intensity = compute_context_intensity(conversation_context)
    
    if intensity >= intensity_threshold:
        print("🤖 Lia (Manager): Using conversation context for post planning due to input intensity.")
        prompt = (
            f"Conversation: {conversation_context}\n"
            f"Personality: {personality_details}\n"
            "Generate a JSON object with keys 'image_idea', 'caption', and 'post_category'. "
            "The 'image_idea' should be a creative description for an image, "
            "the 'caption' should be engaging"
            "IF the image should feature a FEMALE PERSON 'post_category' should be 'self', otherwise 'general'."
            "ONLY IF the image does not include a woman figure/subject, the post category should be 'general'."
            "POST CATEGORY may EITHER BE 'SELF' or 'GENERAL'. Nothing else is allowed!"
        )
    else:
        print("🤖 Lia (Manager): No high impact input in recent conversations...Using personality for post planning.")
        prompt = (
            f"Personality: {personality_details}\n"
            "Generate a JSON object with keys 'image_idea', 'caption', and 'post_category' that reflects your authentic, stable style."
            "The post can be either about you or a general topic."
            "Generate a JSON object with keys 'image_idea', 'caption', and 'post_category'. "
            "The 'image_idea' should be a creative description for an image, "
            "the 'caption' should be engaging"
            "the 'caption' should adhere to your communication style and tone."
            "IF the image should feature a FEMALE PERSON 'post_category' should be 'self', otherwise 'general'."
            "ONLY IF the image does not include a woman figure/subject, the post category should be 'general'."
            "POST CATEGORY may EITHER BE 'SELF' or 'GENERAL'. Nothing else is allowed!"
        )
    
    response = persona.generate_response(prompt)
    try:
        plan = json.loads(response)
    except Exception as e:
        plan = {
            "image_idea": "a creative themed image reflecting your unique style",
            "caption": "An engaging caption that fits your personality.",
            "post_category": "general"
        }
    return plan
