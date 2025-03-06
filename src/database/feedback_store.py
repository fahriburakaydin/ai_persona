import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class FeedbackStore:
    def __init__(self, character_name: str):
        """
        Initializes feedback storage using a JSON file and loads an embedding model.
        """
        self.character_name = character_name
        self.feedback_file = f"src/database/{character_name.lower().replace(' ', '_')}_feedback.json"
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Load embedding model

        # Ensure file exists
        os.makedirs("src/database", exist_ok=True)
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump([], f)

        # Ensure existing feedback has embeddings
        self._update_feedback_with_embeddings()

    def _compute_embedding(self, text: str) -> list:
        """Computes and returns the sentence embedding for a given text."""
        return self.embedding_model.encode(text).tolist()  # Convert NumPy array to list for JSON storage

    def _update_feedback_with_embeddings(self):
        """Checks existing feedback and adds embeddings if missing."""
        with open(self.feedback_file, 'r+') as f:
            feedback_data = json.load(f)
            updated = False

            for entry in feedback_data:
                if "embedding" not in entry:  # Check if the embedding is missing
                    entry["embedding"] = self._compute_embedding(entry["user_input"])
                    updated = True

            if updated:
                f.seek(0)
                json.dump(feedback_data, f, indent=4)
                print("🔄 Updated old feedback entries with embeddings.")

    def store_feedback(self, feedback_entry: dict):
        """Stores user corrections with embeddings."""
        with open(self.feedback_file, 'r+') as f:
            feedback_data = json.load(f)

            # Compute embedding for new feedback entry
            feedback_entry["embedding"] = self._compute_embedding(feedback_entry["user_input"])

            # Avoid duplicate storage
            feedback_data.append(feedback_entry)
            f.seek(0)
            json.dump(feedback_data, f, indent=4)

    def retrieve_feedback(self, user_input: str, n_results: int = 3):
        """Retrieves past feedback using semantic similarity."""
        with open(self.feedback_file, 'r') as f:
            feedback_data = json.load(f)

        if not feedback_data:
            return []

        # Compute embedding for input query
        query_embedding = np.array(self._compute_embedding(user_input))

        # Calculate cosine similarity
        feedback_entries = []
        for entry in feedback_data:
            stored_embedding = np.array(entry["embedding"])
            similarity = np.dot(query_embedding, stored_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding))
            feedback_entries.append((entry, similarity))

        # Sort by highest similarity
        feedback_entries.sort(key=lambda x: x[1], reverse=True)

        return [entry[0] for entry in feedback_entries[:n_results]] if feedback_entries else []
