# src/manager/orchestrator.py

import threading
from src.manager.lia_manager import LiaManager
from src.manager.autonomous_engagement import run_safe_engagement
from src.tools.lia_console import interactive_chat
from src.utils.openai_integration import LiaLama

def run_interactive_manager(persona):
    """
    Initializes Lia's profile and runs her interactive manager.
    """
    first_name = persona.profile.name.split()[0]
    persona_name = first_name.lower()
    display_name = first_name
    manager = LiaManager(persona, persona_name, display_name)
    manager.run()  # This call blocks and handles interactive input.

def run_autonomous_engagement_thread(persona):
    """
    Runs the autonomous engagement module, passing the persona.
    """
    run_safe_engagement(persona)

if __name__ == "__main__":
    # Create the persona instance.
    persona = LiaLama("src/profiles/lia_lama.json", debug=True)
    
    # Start autonomous engagement in a background daemon thread, passing the persona.
    engagement_thread = threading.Thread(target=run_autonomous_engagement_thread, args=(persona,), daemon=True)
    engagement_thread.start()
    
    # Run the interactive manager in the main thread.
    run_interactive_manager(persona)
