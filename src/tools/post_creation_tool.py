from src.utils.post_creator import interactive_post_creation

class PostCreationTool:
    def __init__(self, persona_name: str, display_name: str, persona):
        self.persona_name = persona_name
        self.display_name = display_name
        self.persona = persona

    def run(self, input_data: dict = None) -> dict:
        """
        Runs the interactive post creation dialogue.
        Returns a dictionary with a status message.
        """
        try:
            interactive_post_creation(self.persona_name, self.display_name, self.persona)
            return {"status": "success", "message": "Post creation dialog completed."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
