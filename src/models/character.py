# src/models/character.py

class CharacterProfile:
    def __init__(self, name, appearance, personality_traits, interests, background_story, communication_style, values, user_preferences=None):
        self.name = name
        self.appearance = appearance  
        self.personality_traits = personality_traits
        self.interests = interests
        self.background_story = background_story
        self.communication_style = communication_style
        self.values = values
        self.user_preferences = user_preferences or {}


    def to_dict(self):
        return {
            "name": self.name,
            "appearance": self.appearance,
            "personality_traits": self.personality_traits,
            "interests": self.interests,
            "background_story": self.background_story,
            "communication_style": self.communication_style,
            "values": self.values,
            "user_preferences": self.user_preferences
        
        }
