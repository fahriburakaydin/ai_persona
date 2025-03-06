import json
import openai
import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from src.models.character import CharacterProfile
from src.memory.memory_manager import MemoryManager
from src.memory.feedback_manager import FeedbackManager
from src.memory.personality_manager import PersonalityManager
from src.utils.token_tracker import TokenUsageTracker  # Import Token Tracker

# Load environment variables
load_dotenv()

# Retrieve API key from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

class LiaLama:
    def __init__(self, profile_path, debug=False):
        self.profile = self.load_character_profile(profile_path)
        self.memory = MemoryManager(self.profile.name)
        self.feedback = FeedbackManager(self.profile.name)
        self.personality = PersonalityManager(self.profile.name)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight embedding model
        self.token_tracker = TokenUsageTracker()  # Initialize Token Tracking
        self.debug = debug  # Enable or disable debug mode

    def load_character_profile(self, profile_path):
        with open(profile_path, 'r') as file:
            profile_data = json.load(file)
        return CharacterProfile(
            profile_data["name"],
            profile_data.get("personality_traits", []),
            profile_data.get("interests", []),
            profile_data.get("background_story", ""),
            profile_data.get("communication_style", {}),
            profile_data.get("values", []),
            profile_data.get("user_preferences", {})
        )

    def _compute_embedding(self, text: str) -> np.ndarray:
        """
        Computes the sentence embedding for a given text.
        """
        return self.embedding_model.encode(text)

    def _log_token_usage(self, function_name, response):
        """
        Logs token usage from OpenAI API response.
        """
        if hasattr(response, 'usage'):
            self.token_tracker.log_usage(function_name, response.usage)

    def generate_response(self, user_input):
        """
        Generates a response while allowing Lia's personality to evolve dynamically.
        """
        if not openai.api_key:
            raise ValueError("OpenAI API key is missing! Please set OPENAI_API_KEY in .env file.")

        # Step 1: Retrieve user preferences
        preferences = self.profile.user_preferences

        # Step 2: Retrieve past corrections using semantic similarity
        past_feedback = self.feedback.retrieve_feedback(user_input, n_results=3)
        relevant_correction = next((entry for entry in past_feedback if entry["correction"]), None)

        if relevant_correction:
            correction_instruction = relevant_correction["correction"]
            user_input += f"\n(Note: Apply the correction '{correction_instruction}' naturally.)"

        # Step 3: Retrieve personality evolution trends
        personality_evolution = self.personality.get_top_themes(n_results=5)
        personality_shift_str = "\n".join([f"- {theme}" for theme, _ in personality_evolution])

        # Step 4: Detect implicit feedback for personality adjustment
        if preferences.get("wants_personality_evolution", True):
            feedback_prompt = (
                f"User said: \"{user_input}\".\n"
                f"Does this message contain an instruction for Lia to change behavior or adjust personality? "
                f"If yes, extract the key adjustment. Otherwise, return 'NO CHANGE'."
            )

            feedback_analysis = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": feedback_prompt}]
            )

            self._log_token_usage("feedback_analysis", feedback_analysis)  # Log token usage

            learning_point = feedback_analysis.choices[0].message.content.strip()

            if learning_point != "NO CHANGE":
                print(f"\n💡 Lia is evolving: {learning_point}")
                self.personality.store_theme(learning_point)

        # Step 5: Retrieve relevant short-term memory
        last_conversation = self.memory.retrieve_short_term_memory()

        # Step 6: Apply user preferences for conversation behavior
        if not preferences.get("ask_follow_up_questions", True):
            user_input += "\n(Note: Do not ask the user any questions.)"

        if preferences.get("prefers_direct_answers", False):
            user_input += "\n(Note: Keep responses direct and without unnecessary elaboration.)"

        if preferences.get("simulate_emotions", True):
            user_input += "\n(Note: Respond with human-like emotions.)"

        if preferences.get("allow_sarcasm", True):
            user_input += "\n(Note: Use sarcasm when appropriate. You can be slightly mean.)"

        if preferences.get("flirty", True):  
            user_input += "\n(Note: Be flirty but smart.)"

        # Step 7: Check for topic continuation if the input is too short
        if last_conversation and len(user_input.split()) < 4:
            clarification_prompt = (
                f"User just said: \"{user_input}\" after the conversation: \"{last_conversation}\".\n"
                f"Does this mean the user wants to continue the same topic? Answer only YES or NO."
            )

            clarification_response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": clarification_prompt}]
            )

            self._log_token_usage("clarification_check", clarification_response)  # Log token usage

            should_continue = clarification_response.choices[0].message.content.strip().lower()

            if should_continue == "yes":
                user_input = f"Continue previous topic: {last_conversation}"

        # Step 8: Generate response
        personality_adaptation_prompt = (
            f"Lia has been evolving based on past conversations. Here are recent changes in her personality:\n"
            f"{personality_shift_str}\n\n"
            f"She has learned from the following past conversations:\n"
            f"{last_conversation}\n\n"
            f"Now, generate a response in Lia's current personality, reflecting her evolution.\n"
            f"User: {user_input}"
        )

        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": personality_adaptation_prompt}]
        )

        self._log_token_usage("generate_response", response)  # Log token usage

        generated_response = response.choices[0].message.content.strip()

        # Step 9: Store memory dynamically
        self.memory.store_short_term_memory(f"User: {user_input}\nLia: {generated_response}")
        self.memory.summarize_and_store()

        # Step 10: Debug mode - Show token usage breakdown
        if self.debug:
            self.token_tracker.display_usage_summary()

        return generated_response

    def update_personality(self):
        """
        Adjusts Lia's personality based on repeated conversation themes.
        """
        return self.personality.adjust_personality()
