import json
import os
from collections import deque
from typing import List
from dotenv import load_dotenv
from src.database.memory_store import LongTermMemoryStore  # Import long-term memory handling

load_dotenv()

class MemoryManager:
    def __init__(self, character_name: str, max_short_term_memory: int = 10):
        """
        Initializes the MemoryManager for managing short-term and long-term memory.

        :param character_name: The name of the AI persona.
        :param max_short_term_memory: Maximum number of messages to keep in short-term memory.
        """
        self.character_name = character_name
        self.short_term_memory = deque(maxlen=max_short_term_memory)  # FIFO buffer
        self.memory_store = LongTermMemoryStore(character_name)  # Connect to long-term storage

    def store_short_term_memory(self, conversation_entry: str):
        """
        Stores recent conversation exchanges in short-term memory.
        :param conversation_entry: The user message or assistant response.
        """
        self.short_term_memory.append(conversation_entry)

    def retrieve_short_term_memory(self) -> str:
        """
        Retrieves the most recent short-term memory as a formatted string.
        :return: A formatted conversation history.
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

        # Store in long-term memory
        self.memory_store.store_memory(summary)

        # Clear short-term memory after summarization
        self.short_term_memory.clear()

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

        return response.choices[0].message.content.strip()
