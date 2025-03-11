import os
import shlex
from datetime import datetime, timedelta
from src.utils.openai_integration import LiaLama
from src.utils.intent_detector import detect_intent  # Your existing intent detector
from src.utils.instagram_commands import handle_instagram_command
from src.utils.schedule_commands import schedule_post_job, list_scheduled_jobs, cancel_scheduled_job

# Configurable intent threshold.
INTENT_CONFIDENCE_THRESHOLD = 0.45

# Load Lia's profile.
persona = LiaLama("src/profiles/lia_lama.json", debug=True)
first_name = persona.profile.name.split()[0]
persona_name = first_name.lower()  # internal use.
display_name = first_name         # for display.

def interactive_chat():
    print(f"\n🌀 Welcome to {display_name}'s Console! Chat, provide feedback, or let Lia propose posts. Type 'exit' to quit.\n")
    while True:
        user_input = input("🗨️ You: ")

        # Explicit slash commands.
        if user_input.startswith("/"):
            if user_input.startswith("/schedule"):
                try:
                    args = shlex.split(user_input)
                except ValueError as e:
                    print("Error parsing command:", e)
                    continue
                if len(args) < 2:
                    print("Usage: /schedule <command> [parameters]")
                    continue
                subcommand = args[1].strip().lower()
                if subcommand == "post":
                    if len(args) < 6:
                        print("Usage: /schedule post <time(HH:MM)> <frequency(daily|once)> <image_url> <caption>")
                        continue
                    time_str = args[2]
                    frequency = args[3]
                    image_source = args[4]
                    caption = " ".join(args[5:])
                    result = schedule_post_job(time_str, frequency, image_source, caption, persona_name)
                    print(result)
                elif subcommand == "list":
                    print(list_scheduled_jobs())
                elif subcommand == "cancel":
                    if len(args) < 3:
                        print("Usage: /schedule cancel <job_id>")
                        continue
                    job_id = args[2]
                    print(cancel_scheduled_job(job_id))
                else:
                    print("Unknown schedule command. Supported commands: post, list, cancel")
                continue

            if user_input.startswith("/instagram"):
                result = handle_instagram_command(user_input, persona_name)
                print(result)
                continue

            if user_input.startswith("/generate post"):
                from src.utils.post_creator import interactive_post_creation
                interactive_post_creation(persona_name, display_name)
                continue

        # Natural language input: use intent detection.
        intent_info = detect_intent(user_input)
        detected_intent = intent_info["intent"]
        confidence = intent_info.get("score", 0)
        print(f"Detected intent: {detected_intent}, Confidence score: {confidence:.3f}")

        # If the confidence is too low, default to chat.
        if confidence < INTENT_CONFIDENCE_THRESHOLD:
            detected_intent = "chat"

        if detected_intent == "post":
            approval = input("🤖 Lia: I sense you might want to share a post. Would you like me to propose a post? (yes/no): ").strip().lower()
            if approval in ["yes", "y"]:
                from src.utils.post_creator import interactive_post_creation
                interactive_post_creation(persona_name, display_name)
                continue
            else:
                detected_intent = "chat"

        if detected_intent == "chat":
            response = persona.generate_response(user_input)
            print(f"\n💬 {display_name}: {response}\n")
        else:
            print(f"🤖 Lia: I detected an intent for '{detected_intent}' action, but I'm not handling that yet.")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"\n👋 Exiting {display_name}'s Console. See you next time!\n")
            break

if __name__ == "__main__":
    interactive_chat()
