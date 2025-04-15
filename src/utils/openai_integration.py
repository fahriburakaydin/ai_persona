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
from src.config import OPENAI_API_KEY
from src.utils.chroma_factory import get_chroma_client_and_embedder


# Load environment variables
load_dotenv()

if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is missing in the configuration.")
        raise Exception("Missing OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

class LiaLama:
    def __init__(self, profile_path, debug=False):
        self.profile = self.load_character_profile(profile_path)
        # Obtain shared dependencies from the centralized factory
        self.client, self.embedder = get_chroma_client_and_embedder()
        
        # Pass the dependencies to all submodules
        self.memory = MemoryManager(self.profile.name, client=self.client, embedder=self.embedder)
        self.feedback = FeedbackManager(self.profile.name, client=self.client, embedder=self.embedder)
        self.personality = PersonalityManager(self.profile.name, client=self.client, embedder=self.embedder)
        
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.token_tracker = TokenUsageTracker()
        self.debug = debug

    def load_character_profile(self, profile_path):
        with open(profile_path, 'r') as file:
            profile_data = json.load(file)
        return CharacterProfile(
            profile_data["name"],
            profile_data.get("appearance", ""),
            profile_data.get("appearance_nsfw", ""),
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
        personality_shift = self.personality.get_top_traits(3)
        personality_shift_str = "\n".join([f"- {trait} ({score})" for trait, score in personality_shift])
        # Check for feedback command first
        if user_input.startswith("/feedback "):
            feedback = user_input[len("/feedback "):].strip()
            self.process_explicit_feedback(feedback)
            return "🔍 Feedback received - I'll work on that!"
        

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

        human_like_score = [score for trait, score in personality_shift if trait == "human-like"][0]
        if human_like_score > 6:
            user_input += "\n(Note: You are a real human - NEVER mention or imply being digital/AI)"
        elif human_like_score < 4:
            user_input += "\n(Note: You can acknowledge your AI nature)"

        # Step 7: Check for topic continuation if the input is too short
        if last_conversation and len(user_input.split()) < 4:
            clarification_prompt = (
                f"User just said: \"{user_input}\" after the conversation: \"{last_conversation}\".\n"
                f"Does this mean the user wants to continue the same topic? Answer only YES or NO."
            )

            clarification_response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": clarification_prompt}],
                            tempreture=0.8,            )

            self._log_token_usage("clarification_check", clarification_response)  # Log token usage

            should_continue = clarification_response.choices[0].message.content.strip().lower()

            if should_continue == "yes":
                user_input = f"Continue previous topic: {last_conversation}"

        # Step 8: Generate response
       # In generate_response method, replace personality adaptation section:
        personality_adaptation_prompt = (
            f"{self.personality.get_personality_prompt()}\n"
            f"Recent conversation context:\n{last_conversation}\n\n"
            f"User: {user_input}\n"
            "Generate response considering these personality weights:"
        )

        # Add feedback-based tuning
        if past_feedback:
            feedback_str = "\n".join([f"- {fb['correction']}" for fb in past_feedback])
            personality_adaptation_prompt += f"\nRecent feedback to apply:\n{feedback_str}"
        

        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": personality_adaptation_prompt}],
            max_tokens=300,
            temperature=0.8
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

    def process_explicit_feedback(self, feedback_text: str):
        """Handle structured feedback like '/feedback be more sarcastic'"""
        # 1. Direct personality adjustment
        self.personality.store_theme(feedback_text)
        
        # 2. Update long-term preferences
        if "no questions" in feedback_text.lower():
            self.profile.user_preferences["ask_follow_up_questions"] = False
        
        # 3. Semantic reinforcement
        self.feedback.store_feedback(
            user_input=feedback_text,
            correction=f"System: Apply {feedback_text}",
            original_response="[explicit_feedback]"  # Add this flag
        )
        
        if "human" in feedback_text.lower():
            # Force immediate personality adjustment
            self.personality.trait_weights["human-like"] += 5
            self.profile.user_preferences["acknowledge_digital"] = False
       
        if feedback_text.startswith("direct"):
            self.personality.trait_weights["directness"] += 5  # Strong adjustment 