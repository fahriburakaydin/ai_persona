
from src.utils.openai_integration import LiaLama

lia = LiaLama("src/profiles/lia_lama.json")

print(lia.generate_response("Tell me a joke!"))  # Should retrieve or generate a joke
print(lia.generate_response("Tell me another one!"))  # Should generate a different joke
print(lia.generate_response("Tell me a joke about animals!"))  # Should be different but related
print(lia.generate_response("Give me an inspirational quote!"))  # Should retrieve a fresh quote
print(lia.generate_response("One more!")) 