import json
import os
from collections import deque
from typing import List
from dotenv import load_dotenv
from src.utils.token_tracker import TokenUsageTracker  # Import Token Tracker
from src.database.memory_store import LongTermMemoryStore

load_dotenv()

class MemoryManager:
    def __init__(self, character_name: str, max_short_term_memory: int = 10, debug: bool = True):
        """
        Initializes the MemoryManager for managing short-term and long-term memory.
        """
        self.character_name = character_name
        self.short_term_memory = deque(maxlen=max_short_term_memory)  # FIFO buffer
        self.memory_store = LongTermMemoryStore(character_name)  # Connect to long-term storage
        self.token_tracker = TokenUsageTracker()  # Initialize Token Tracking
        self.debug = debug  # Enable or disable debug mode

    def _log_token_usage(self, function_name, response):
        """
        Logs token usage from OpenAI API response.
        """
        if hasattr(response, 'usage'):
            print(f"Logging Token Usage for {function_name}: {response.usage}")  # Debugging
            self.token_tracker.log_usage(function_name, response.usage)


    def store_short_term_memory(self, conversation_entry: str):
        """
        Stores recent conversation exchanges in short-term memory.
        """
        self.short_term_memory.append(conversation_entry)

    def retrieve_short_term_memory(self) -> str:
        """
        Retrieves the most recent short-term memory as a formatted string.
        """
        if not self.short_term_memory:
            return "No recent memory available."
        return "\n".join(self.short_term_memory)

    def summarize_and_store(self):
        """
        Summarizes long conversations and transfers key points to long-term memory.
        """
        if len(self.short_term_memory) < 5:
            return  # Skip summarization if conversation is short

        conversation_text = "\n".join(self.short_term_memory)

        # Generate summary using the LLM
        summary_prompt = f"Summarize the key points from this conversation for future reference:\n\n{conversation_text}"
        summary = self.generate_summary(summary_prompt)

        #Ensure the correct summary is stored
        if summary:
            self.memory_store.store_memory(summary)
            self.short_term_memory.clear()  # Clear short-term memory after summarization
            print(f"\n(Lia has updated her long-term memory! 🧠) {summary}")

    def generate_summary(self, prompt: str) -> str:
        """
        Uses the LLM to generate a summary of past conversations.
        """
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")

        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        print(f"Summary Generation Token Usage: {response.usage}")  # Debugging

        self._log_token_usage("summary_generation(memoryMngr)", response)  # Explicitly call logging method
        return response.choices[0].message.content.strip()
