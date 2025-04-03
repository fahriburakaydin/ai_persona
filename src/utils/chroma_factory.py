# src/utils/chroma_factory.py
import chromadb
from chromadb.utils import embedding_functions

DATABASE_PATH = "./memory_store"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Cache the client and embedder to enforce a singleton
_client = None
_embedder = None

def get_chroma_client_and_embedder():
    """
    Returns a singleton instance of the ChromaDB client and embedding function.
    """
    global _client, _embedder
    if _client is None or _embedder is None:
        _client = chromadb.PersistentClient(path=DATABASE_PATH)
        _embedder = embedding_functions.SentenceTransformerEmbeddingFunction(EMBEDDING_MODEL)
    return _client, _embedder
