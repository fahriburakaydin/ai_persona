import chromadb
from chromadb.utils import embedding_functions

class FeedbackStore:
    def __init__(self, character_name: str):
        self.character_name = character_name.lower().replace(' ', '_')
        self.client = chromadb.PersistentClient(path="./memory_store")
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name=f"{self.character_name}_feedback",
            embedding_function=self.embedder
        )

    def store_feedback(self, feedback_entry: dict):
        """Handle both feedback types with optional fields"""
        
        required_fields = ["user_input"]
        if not all(field in feedback_entry for field in required_fields):
            raise ValueError("Feedback entry missing required fields")
        
        # Add default for missing original_response
        if "original_response" not in feedback_entry:
            feedback_entry["original_response"] = "[system]"
            
            doc_id = f"fb_{len(self.collection.get()['ids']) + 1}"
            self.collection.add(
                documents=[feedback_entry["user_input"]],
                metadatas=[{"correction": feedback_entry["correction"]}],
                ids=[doc_id]
            )

    def retrieve_feedback(self, query: str, n_results: int = 3) -> list:
        """Semantic search for relevant feedback"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["metadatas"]
        )
        return [{"correction": m["correction"]} for m in results["metadatas"][0]]