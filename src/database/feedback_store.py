# src/database/feedback_store.py
import chromadb
from chromadb.utils import embedding_functions

class FeedbackStore:
    def __init__(self, character_name: str, client: chromadb.ClientAPI, embedder: embedding_functions.EmbeddingFunction):
        self.character_name = character_name.lower().replace(' ', '_')
        self.client = client
        self.embedder = embedder
        self.collection = self.client.get_or_create_collection(
            name=f"{self.character_name}_feedback",
            embedding_function=self.embedder
        )

    def store_feedback(self, feedback_entry: dict):
        """Store feedback entry into the database."""
        required_fields = ["user_input"]
        if not all(field in feedback_entry for field in required_fields):
            raise ValueError("Feedback entry missing required fields")

        if "original_response" not in feedback_entry:
            feedback_entry["original_response"] = "[system]"

        doc_id = f"fb_{len(self.collection.get()['ids']) + 1}"
        self.collection.add(
            documents=[feedback_entry["user_input"]],
            metadatas=[{"correction": feedback_entry["correction"]}],
            ids=[doc_id]
        )

    def retrieve_feedback(self, query: str, n_results: int = 3) -> list:
        """Perform semantic search for feedback."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["metadatas"]
        )
        return [{"correction": m["correction"]} for m in results["metadatas"][0]] if results["metadatas"] else []
