# tests/conftest.py
import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """This ensures pytest always loads your .env file."""
    load_dotenv()

@pytest.fixture(scope="session")
def api_key_available():
    """Check if OpenAI API key is available for testing."""
    return os.getenv("OPENAI_API_KEY") is not None

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for testing."""
    return {
        "choices": [{
            "message": {
                "content": "Great job on your fitness progress! Keep pushing towards your goals!"
            }
        }]
    }

@pytest.fixture
def mock_agents_response():
    """Mock Agents SDK response for testing."""
    return {
        "messages": [{
            "content": "Excellent work! You're making amazing progress on your health journey!"
        }]
    }
