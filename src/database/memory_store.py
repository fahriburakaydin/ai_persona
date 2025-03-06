import chromadb
from chromadb.utils import embedding_functions
from typing import List

class LongTermMemoryStore:
    """Class to store and retrieve long-term memories for a character"""

    def __init__(self, character_name: str):
        """Initialize the memory store for a character"""
        self.character_name = character_name.lower().replace(' ', '_')
        self.client = chromadb.PersistentClient(path="./memory_store")
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name=f"{self.character_name}_memory",
            embedding_function=self.embedder
        )

    def store_memory(self, memory_entry: str):
        """Store memory with automatic embedding"""
        memory_id = f"mem_{len(self.collection.get()['ids']) + 1}"
        self.collection.add(
            documents=[memory_entry],
            ids=[memory_id]
        )

    def retrieve_memories(self, query: str, n_results: int = 5) -> List[str]:
        """Semantic search for relevant memories"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]