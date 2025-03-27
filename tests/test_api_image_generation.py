# tests/test_api_image_generation.py
import os
import tempfile
import requests
from src.utils.api_image_generation import query, generate_image

# Create a fake response class to simulate requests responses
class FakeResponse:
    def __init__(self, status_code, content, json_data=None):
        self.status_code = status_code
        self._content = content
        self._json = json_data

    def json(self):
        if self._json is not None:
            return self._json
        raise ValueError("No JSON available")

    @property
    def content(self):
        return self._content

# Fake requests.post that simulates a successful response
def fake_post_success(url, headers, json):
    return FakeResponse(200, b"fake_image_data")

# Fake requests.post that simulates a failure response
def fake_post_failure(url, headers, json):
    return FakeResponse(500, b"", {"error": "test error"})

def test_query_success(monkeypatch):
    monkeypatch.setattr(requests, "post", fake_post_success)
    data = query("test prompt", seed=42, max_retries=1)
    assert data == b"fake_image_data"

def test_generate_image(monkeypatch):
    monkeypatch.setattr(requests, "post", fake_post_success)
    image_path = generate_image("test prompt", seed=42)
    # Verify that the temporary file exists and its content is as expected
    with open(image_path, "rb") as f:
        content = f.read()
    assert content == b"fake_image_data"
    # Clean up the temporary file
    os.remove(image_path)

def test_query_failure(monkeypatch):
    monkeypatch.setattr(requests, "post", fake_post_failure)
    import pytest
    with pytest.raises(Exception) as excinfo:
        query("test prompt", seed=42, max_retries=1)
    assert "Error" in str(excinfo.value)
