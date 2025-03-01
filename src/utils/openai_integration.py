import json
import openai
import os
from dotenv import load_dotenv
from src.models.character import CharacterProfile
from src.memory.memory_manager import MemoryManager
from src.memory.feedback_manager import FeedbackManager
from src.memory.personality_manager import PersonalityManager

# Load environment variables
load_dotenv()

# Retrieve API key from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

class LiaLama:
    def __init__(self, profile_path):
        self.profile = self.load_character_profile(profile_path)
        self.memory = MemoryManager(self.profile.name)
        self.feedback = FeedbackManager(self.profile.name)
        self.personality = PersonalityManager(self.profile.name)

    def load_character_profile(self, profile_path):
        with open(profile_path, 'r') as file:
            profile_data = json.load(file)
        return CharacterProfile(
            profile_data["name"],
            profile_data["personality_traits"],
            profile_data["interests"],
            profile_data["background_story"],
            profile_data["communication_style"],
            profile_data["values"]
        )

    def generate_response(self, user_input):
        """
        Generates a response based on memory, feedback, and key learnings.
        """
        if not openai.api_key:
            raise ValueError("OpenAI API key is missing! Please set OPENAI_API_KEY in .env file.")

        # Step 1: Retrieve past corrections and look for relevant ones
        past_feedback = self.feedback.retrieve_feedback(user_input, n_results=3)
        relevant_correction = next((entry for entry in past_feedback if entry["correction"]), None)

        # Handle vague requests by recalling last conversation topic
        last_conversation_topic = self.memory.retrieve_short_term_memory()[-1] if self.memory.retrieve_short_term_memory() else None
        if last_conversation_topic and len(user_input.split()) < 4:
            print("\n(Lia is analyzing user intent... 🤔)")

            # Ask the LLM if this input is likely referring to the previous topic
            clarification_prompt = (
                f"User just said: \"{user_input}\" in response to the last conversation: \"{last_conversation_topic}\".\n"
                f"Does this mean the user wants to continue the same topic (e.g., another joke, another quote, another response on the same subject)? "
                f"Answer only YES or NO."
            )

            clarification_response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": clarification_prompt}]
            )

            should_continue = clarification_response.choices[0].message.content.strip().lower()

            if should_continue == "yes":
                topic_parts = last_conversation_topic.split(':', 1)
                if len(topic_parts) > 1:
                    user_input = f"Another {topic_parts[1].strip()}"
                else:
                    user_input = "Give me something new!"

        # If a relevant correction exists, apply it contextually
        if relevant_correction:
            correction_instruction = relevant_correction["correction"]

            # Ensure topic relevance (jokes for jokes, quotes for quotes, etc.)
            if any(keyword in user_input.lower() for keyword in ["joke", "funny", "laugh"]):
                if "joke" in relevant_correction["user_input"].lower():
                    print("\n(Lia has learned a joke-related correction! ✅)")

                    refined_prompt = (
                        f"{self.profile.name} has learned this joke-related correction: \"{correction_instruction}\" "
                        f"and should apply it while generating a **new** joke to avoid repetition.\n"
                        f"User: {user_input}"
                    )

                    response = openai.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[{"role": "system", "content": refined_prompt}]
                    )

                    corrected_response = response.choices[0].message.content.strip()

                    # Store the improved response for future learning
                    self.feedback.store_feedback(user_input, corrected_response, "👍")

                    return corrected_response

            # General correction application for other types of responses
            print("\n(Lia has learned! Applying the correction... ✅)")

            refined_prompt = (
                f"{self.profile.name} has learned this correction pattern: \"{correction_instruction}\" "
                f"and should apply it naturally to generate a fresh response.\n"
                f"User: {user_input}"
            )

            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": refined_prompt}]
            )

            corrected_response = response.choices[0].message.content.strip()

            # Store the improved response to reinforce learning
            self.feedback.store_feedback(user_input, corrected_response, "👍")

            return corrected_response

        # Step 2: Retrieve conversation memory and key learnings
        recent_chat_context = self.memory.retrieve_short_term_memory()
        past_takeaways = self.memory.memory_store.retrieve_memories(n_results=3)
        past_takeaways_str = "\n".join([str(mem) for mem in past_takeaways])

        # Step 3: Construct a natural prompt when no corrections exist
        prompt = (
            f"{self.profile.name} is a digital being with a {self.profile.communication_style['tone']}.\n"
            f"She is known for being {', '.join(self.profile.personality_traits)} and has a deep interest in {', '.join(self.profile.interests)}.\n\n"
            f"Background: {self.profile.background_story}\n\n"
            f"🔹 **Recent Chat Context**:\n{recent_chat_context}\n\n"
            f"🔹 **Past Learnings**:\n{past_takeaways_str}\n\n"
            f"Now, respond to this input in her signature style:\n"
            f"User: {user_input}"
        )

        # Step 4: Generate a new response
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}]
        )

        generated_response = response.choices[0].message.content
        self.memory.store_short_term_memory(f"User: {user_input}\nLia: {generated_response}")

        print(f"\nLia Lama: {generated_response}")  # Show Lia's response

        # Step 5: Ask for feedback
        rating = input("\nDid Lia respond well? (Type 👍/👎 or 'y'/'n'): ").strip()
        rating = "👍" if rating.lower() in ["y", "👍"] else "👎"

        correction = None
        if rating == "👎":
            correction = input("Provide an instruction for Lia to improve next time: ").strip()

        # Step 6: Store feedback for future learning
        self.feedback.store_feedback(user_input, generated_response, rating, correction)

        return generated_response

    def update_personality(self):
        """
        Adjusts Lia's personality based on repeated conversation themes.
        """
        print(self.personality.adjust_personality())
