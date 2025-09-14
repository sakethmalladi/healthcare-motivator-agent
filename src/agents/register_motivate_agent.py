import sys
from pathlib import Path

# Add the project root to sys.path so 'src' can be imported
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

import yaml
from openai import OpenAI
from src.tools.search_web import search_web
from src.tools.search_youtube import search_youtube
from src.config.settings import OPENAI_API_KEY  # import your key from settings

def register_motivate_user_agent():
    # Initialize OpenAI client with API key
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Load YAML spec from same folder as this script
    yaml_path = Path(__file__).parent / "motivate_user_agent.yaml"
    with open(yaml_path) as f:
        spec = yaml.safe_load(f)

    # Define tools in JSON-serializable format
    tools = [
        {
            "type": "tool",
            "name": "search_web",
            "description": "Search DuckDuckGo for helpful motivation/health articles",
            "parameters": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 3},
            },
        },
        {
            "type": "tool",
            "name": "search_youtube",
            "description": "Search YouTube for motivational or instructional videos",
            "parameters": {
                "query": {"type": "string"}
            },
        },
    ]

    assistant = client.beta.assistants.create(
        name=spec["name"],
        description=spec["description"],
        model=spec["model"],
        instructions=spec["instructions"],
        tools=tools,  # now using "type": "function"
    )

    print("Agent registered:", assistant.id)
    return assistant

if __name__ == "__main__":
    register_motivate_user_agent()