from src.utils.openai_integration import LiaLama

# Load Lia's profile
lia = LiaLama("src/profiles/lia_lama.json", debug=True)

def interactive_chat():
    """
    Starts an interactive console to chat with Lia, observe learning, and provide real-time feedback.
    """
    print("\n🌀 Welcome to Lia's Console! You can chat, observe learning, and give feedback. Type 'exit' to quit.\n")

    while True:
        user_input = input("🗨️ You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\n👋 Exiting Lia's Console. See you next time!\n")
            break

        response = lia.generate_response(user_input)
        print(f"\n💬 Lia: {response}\n")

interactive_chat()
