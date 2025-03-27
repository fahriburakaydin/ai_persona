# tests/test_intent_detector.py
from src.utils.intent_detector import detect_intent

def test_detect_intent():
    # Provide a sample user input that should trigger a known intent
    result = detect_intent("I want to post a new photo")
    # Check that the result contains 'intent' and 'score'
    assert "intent" in result
    assert "score" in result
    # Verify that the detected intent is one of the candidate intents
    candidate_intents = ["post", "comment", "follow", "dm", "schedule", "chat"]
    assert result["intent"] in candidate_intents
