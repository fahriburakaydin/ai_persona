from transformers import pipeline

# Initialize zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define candidate intents
CANDIDATE_INTENTS = ["post", "comment", "follow", "dm", "schedule", "chat"]

def detect_intent(user_input: str) -> dict:
    """
    Uses zero-shot classification to determine the intent of the user input.
    Returns a dict with the detected "intent" and its "score".
    """
    # Run the zero-shot classifier on the user input with our candidate intents
    result = classifier(user_input, candidate_labels=CANDIDATE_INTENTS, multi_label=False)
    # The highest scoring label is considered the detected intent
    intent = result["labels"][0]
    score = result["scores"][0]
    return {"intent": intent, "score": score, "raw": result}

if __name__ == "__main__":
    sample_text = input("Enter a sample user input: ")
    intent_info = detect_intent(sample_text)
    print("Detected intent:", intent_info["intent"])
    print("Confidence score:", intent_info["score"])
    print("Raw output:", intent_info["raw"])
