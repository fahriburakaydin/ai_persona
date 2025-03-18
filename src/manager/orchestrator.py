# src/manager/orchestrator.py

import threading
from src.manager.lia_manager import LiaManager
from src.manager.autonomous_engagement import run_autonomous_engagement
from src.utils.openai_integration import LiaLama

def run_interactive_manager():
    """
    Runs the interactive Lia manager.
    This function starts an interactive console where you can provide input.
    """
    # Load Lia's profile and initialize her manager.
    persona = LiaLama("src/profiles/lia_lama.json", debug=True)
    first_name = persona.profile.name.split()[0]
    persona_name = first_name.lower()
    display_name = first_name
    manager = LiaManager(persona, persona_name, display_name)
    # This will block and allow you to interact.
    manager.run()

def run_autonomous_engagement():
    """
    Runs the autonomous engagement module.
    This function will continuously monitor and engage with posts in the background.
    """
    run_autonomous_engagement()

if __name__ == "__main__":
    # Start the autonomous engagement in a background daemon thread.
    engagement_thread = threading.Thread(target=run_autonomous_engagement, daemon=True)
    engagement_thread.start()
    
    # Run the interactive manager in the main thread.
    run_interactive_manager()
