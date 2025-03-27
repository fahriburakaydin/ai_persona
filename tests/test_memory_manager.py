# tests/test_memory_manager.py
from src.memory.memory_manager import MemoryManager

def test_short_term_memory():
    # Create a MemoryManager instance with a small max capacity for testing
    mm = MemoryManager("TestCharacter", max_short_term_memory=5, debug=False)
    
    # Initially, short-term memory is empty
    assert mm.retrieve_short_term_memory() == "No recent memory available."
    
    # Store one message and check it is retrieved
    mm.store_short_term_memory("Hello World")
    result = mm.retrieve_short_term_memory()
    assert "Hello World" in result

    # Store multiple messages and verify the buffer does not exceed the limit
    for i in range(10):
        mm.store_short_term_memory(f"Message {i}")
    # The deque should only hold 5 items (max_short_term_memory is 5)
    result = mm.retrieve_short_term_memory().split("\n")
    assert len(result) <= 5
