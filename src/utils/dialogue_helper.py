# src/utils/dialogue_helper.py

def generate_followup_question(persona, provided_inputs: dict, missing_inputs: list, conversation_context: str) -> str:
    """
    Generates a natural follow-up question for missing inputs based on the conversation context.
    
    Parameters:
      - persona: an instance of LiaLama (to generate responses)
      - provided_inputs: dict of inputs already gathered (e.g., {"post_type": "now"})
      - missing_inputs: list of input keys that are still missing (e.g., ["caption"])
      - conversation_context: a string summarizing recent conversation context
    
    Returns:
      A natural, friendly follow-up question as a string.
    """
    prompt = (
        "You are Lia, a witty, insightful, and fully autonomous social media influencer. "
        f"Based on the inputs you have gathered so far: {provided_inputs}, you still need the following: {missing_inputs}. "
        f"Considering the recent conversation context: {conversation_context}, "
        "generate a natural, friendly follow-up question to ask the user for the missing information."
    )
    question = persona.generate_response(prompt)
    return question
