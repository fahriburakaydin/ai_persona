# src/memory/feedback_manager.py
import os
import json
from src.database.feedback_store import FeedbackStore
from dotenv import load_dotenv

load_dotenv()

class FeedbackManager:
    def __init__(self, character_name: str, client, embedder):
        """
        Initializes feedback memory storage with injected dependencies.
        
        Args:
            character_name: The name of the character.
            client: The shared ChromaDB client.
            embedder: The shared embedding function.
        """
        self.character_name = character_name
        self.feedback_store = FeedbackStore(character_name, client, embedder)

    def store_feedback(self, user_input: str, correction: str = None, original_response: str = "[system]"):
        """
        Stores feedback by creating a feedback entry and saving it via FeedbackStore.
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
        Returns a summary of all stored feedback.
        """
        return "Feedback summary not implemented yet."
