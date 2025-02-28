import os
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

class LongTermMemoryStore:
    def __init__(self, character_name: str):
        """
        Initializes long-term memory storage using a JSON file.
        """
        self.character_name = character_name
        self.memory_dir = "src/database"
        self.memory_file = f"{self.memory_dir}/{character_name.lower().replace(' ', '_')}_memory.json"

        # Ensure the directory exists before creating the file
        os.makedirs(self.memory_dir, exist_ok=True)

        # Ensure file exists
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)

    def store_memory(self, memory_entry: str):
        """
        Stores summarized long-term memory into the database.
        """
        with open(self.memory_file, 'r+') as f:
            memories = json.load(f)
            memories.append(memory_entry)
            f.seek(0)
            json.dump(memories, f, indent=4)

    def retrieve_memories(self, n_results: int = 5) -> List[str]:
        """
        Retrieves the last N memory entries.
        """
        with open(self.memory_file, 'r') as f:
            memories = json.load(f)
            return memories[-n_results:] if len(memories) > n_results else memories
