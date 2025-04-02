# app.py
import os
from flask import Flask, jsonify
from src.manager.lia_manager import LiaManager
from src.utils.openai_integration import LiaLama

app = Flask(__name__)

@app.route('/trigger_post', methods=['GET'])
def trigger_post():
    try:
        # Initialize Lia's persona
        persona = LiaLama("src/profiles/lia_lama.json", debug=True)
        persona_name = persona.profile.name.split()[0].lower()
        manager = LiaManager(persona, persona_name)
        # Check if it's time to post using your existing logic
        if manager.should_post():
            manager.create_post_autonomously()
            return jsonify({"status": "success", "message": "Post created."}), 200
        else:
            return jsonify({"status": "ok", "message": "No post due yet."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "Lia is running and healthy."

if __name__ == "__main__":
    # Start the Flask server on port 8080 (default for Cloud Run)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
