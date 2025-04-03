import chromadb
from collections import defaultdict
from chromadb.utils import embedding_functions

class PersonalityManager:
    def __init__(self, character_name: str, client: chromadb.ClientAPI, embedder: embedding_functions.EmbeddingFunction):
        self.character_name = character_name.lower().replace(' ', '_')
    
        self.client = client
        self.embedder = embedder
        self.collection = self.client.get_or_create_collection(
            name=f"{self.character_name}_personality",
            embedding_function=self.embedder
        )
        
        # Initialize trait weights
        self.trait_weights = defaultdict(int)
        self.base_traits = {
            "thoughtful": 5, 
            "playful": 5, 
            "sarcastic": 5,
            "inspiring": 5,
            "adventurous": 5,
            "human-like": 8
        }

    def store_theme(self, theme: str):
        """Store theme and update trait weights"""
        self.collection.add(
            documents=[theme],
            ids=[f"theme_{len(self.collection.get()['ids']) + 1}"]
        )
        
        # Update weights based on theme content
        theme_lower = theme.lower()
        if "philosophy" in theme_lower:
            self.trait_weights["thoughtful"] += 2
        elif "humor" in theme_lower:
            self.trait_weights["playful"] += 2
        elif "travel" in theme_lower:
            self.trait_weights["adventurous"] += 2
        elif "motivation" in theme_lower:
            self.trait_weights["inspiring"] += 2
        elif "human" in theme_lower or "real person" in theme_lower:
            self.trait_weights["human-like"] += 3

    def get_top_traits(self, n_results: int = 3) -> list:
        """Get current dominant traits"""
        weighted = {k: v + self.trait_weights.get(k, 0) 
                   for k, v in self.base_traits.items()}
        return sorted(weighted.items(), key=lambda x: x[1], reverse=True)[:n_results]

    def get_personality_prompt(self) -> str:
        """Generate dynamic personality prompt"""
        top_traits = self.get_top_traits()
        return f"Lia's current personality weights: {', '.join([f'{trait} ({score})' for trait, score in top_traits])}"