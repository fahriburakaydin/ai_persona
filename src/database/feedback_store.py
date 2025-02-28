import os
import json
import hashlib
from typing import List
from dotenv import load_dotenv

load_dotenv()

class FeedbackStore:
    def __init__(self, character_name: str):
        """
        Initializes feedback storage using a JSON file.
        """
        self.character_name = character_name
        self.feedback_file = f"src/database/{character_name.lower().replace(' ', '_')}_feedback.json"

        # Ensure the directory exists before creating the file
        os.makedirs("src/database", exist_ok=True)

        # Ensure file exists
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump([], f)

    def _generate_hash(self, text: str) -> str:
        """
        Generates a hash for a given text input to ensure unique storage.
        """
        return hashlib.md5(text.encode()).hexdigest()

    def store_feedback(self, feedback_entry: dict):
        """
        Stores user corrections in long-term memory.
        """
        with open(self.feedback_file, 'r+') as f:
            feedback_data = json.load(f)

            # Generate a unique hash key for the correction
            correction_id = self._generate_hash(feedback_entry["user_input"])
            feedback_entry["id"] = correction_id

            # Avoid duplicate storage
            existing_ids = {item["id"] for item in feedback_data}
            if correction_id not in existing_ids:
                feedback_data.append(feedback_entry)

            f.seek(0)
            json.dump(feedback_data, f, indent=4)

    def retrieve_feedback(self, user_input: str, n_results: int = 1):
            """
            Retrieves past feedback relevant to a given input.
            Uses similarity matching instead of exact matching.
            """
            with open(self.feedback_file, 'r') as f:
                feedback_data = json.load(f)

            # Use semantic similarity instead of exact matches
            from difflib import get_close_matches

            # Extract all stored user inputs
            stored_inputs = [entry["user_input"] for entry in feedback_data]

            # Find the closest matching past correction
            similar_inputs = get_close_matches(user_input, stored_inputs, n=n_results, cutoff=0.6)

            similar_feedback = [entry for entry in feedback_data if entry["user_input"] in similar_inputs]

            return similar_feedback[:n_results] if similar_feedback else []

    
    def get_feedback_summary(self):
        """
        Retrieves a summary of stored corrections.
        """
        with open(self.feedback_file, 'r') as f:
            feedback_data = json.load(f)
        
        return feedback_data
