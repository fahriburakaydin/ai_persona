import os
import json
from src.database.feedback_store import FeedbackStore
from dotenv import load_dotenv

load_dotenv()

class FeedbackManager:
    def __init__(self, character_name: str):
        """
        Initializes feedback memory storage.
        """
        self.character_name = character_name
        self.feedback_store = FeedbackStore(character_name)

    def store_feedback(self, user_input: str, original_response: str, correction: str = None):
        """
        Stores user feedback and corrections.
        """
        feedback_entry = {
            "user_input": user_input,
            "original_response": original_response,
            "correction": correction
        }

        self.feedback_store.store_feedback(feedback_entry)

    def retrieve_feedback(self, user_input: str, n_results: int = 1):
        """
        Retrieves past corrections for a similar user input using semantic similarity.
        """
        return self.feedback_store.retrieve_feedback(user_input, n_results)

    def get_feedback_summary(self):
        """
        Displays a summary of all stored feedback.
        """
        return self.feedback_store.get_feedback_summary()
