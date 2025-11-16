import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")

# Models and AI settings
PLANNING_MODEL = os.getenv("PLANNING_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Assistants (optional)
PLANNING_USE_ASSISTANT = os.getenv("PLANNING_USE_ASSISTANT", "0") in ("1", "true", "True")
PLANNING_ASSISTANT_ID = os.getenv("PLANNING_ASSISTANT_ID")