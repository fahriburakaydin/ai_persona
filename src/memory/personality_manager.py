import chromadb
from collections import Counter

class PersonalityManager:
    def __init__(self, character_name):
        """
        Manages Lia's evolving personality based on conversation insights.
        """
        self.character_name = character_name
        self.client = chromadb.PersistentClient(path=f"./memory_store/{character_name}")
        sanitized_name = character_name.strip().replace(" ", "_")  # Remove spaces
        self.collection = self.client.get_or_create_collection(name=f"{sanitized_name}_personality")


    def store_theme(self, theme):
        """
        Stores a conversation theme as a memory entry.
        """
        memory_id = f"theme_{len(self.collection.get()['ids']) + 1}"
        self.collection.add(
            documents=[theme],
            metadatas=[{"type": "theme"}],
            ids=[memory_id]
        )

    def get_top_themes(self, n_results=3):
        """
        Retrieves the most common conversation themes to adjust personality.
        """
        results = self.collection.get()
        themes = [metadata["type"] for metadata in results["metadatas"] if "type" in metadata]
        theme_counts = Counter(themes)
        return theme_counts.most_common(n_results)

    def adjust_personality(self):
        """
        Adjusts Lia's personality based on dominant themes.
        """
        top_themes = self.get_top_themes()

        if not top_themes:
            return "No major personality shifts detected yet."

        print("\n🔄 Adjusting Lia's personality based on conversation trends...")
        personality_shift = []

        for theme, count in top_themes:
            if theme == "philosophy":
                personality_shift.append("Lia becomes more thoughtful and deep-thinking.")
            elif theme == "humor":
                personality_shift.append("Lia adopts a more playful and witty tone.")
            elif theme == "motivation":
                personality_shift.append("Lia becomes more inspiring and uplifting.")
            elif theme == "travel":
                personality_shift.append("Lia speaks more about adventure and cultural experiences.")

        return "\n".join(personality_shift) if personality_shift else "No major changes needed."
