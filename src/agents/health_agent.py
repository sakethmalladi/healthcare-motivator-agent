# src/agents/health_agent.py

import os
from openai import OpenAI
from src.models.health_models import MotivationRequest, MotivationResponse
from src.tools.search_web import search_web
from src.tools.search_youtube import search_youtube

def get_client():
    """Create OpenAI client."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(previous_data: str, current_data: str, action_taken: str, next_action: str, custom_instruction: str, goal: str, progress: str) -> str:
    """Build motivation prompt for LLM."""
    return f"""
You are a supportive health assistant.
The user has shared their health progress:

Previous Data: {previous_data}
Current Data: {current_data}
Action Taken: {action_taken}
Next Action: {next_action}
Goal: {goal}
Progress: {progress}

Instructions:
{custom_instruction}

Provide motivational advice in a short, positive tone and suggest helpful web articles and YouTube videos.
"""

async def run_health_agent(request: MotivationRequest) -> MotivationResponse:
    """Run the health agent using OpenAI + API-free Web/YouTube searches."""
    client = get_client()

    prompt = build_prompt(
        previous_data=request.previous_data,
        current_data=request.current_data,
        action_taken=request.action_taken,
        next_action=request.next_action,
        custom_instruction=request.custom_instruction,
        goal=request.goal,
        progress=request.progress
    )

    # Call OpenAI chat completion
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Motivate me today based on my health data."}
        ]
    )

    # Fallback if the model returns empty
    motivation_text = response.choices[0].message.content
    if not motivation_text or motivation_text.strip() == "":
        motivation_text = f"Great job! You're making progress towards your goal: {request.goal}. Keep it up!"

    # Get top 3 web and YouTube results
    web_results = search_web(f"{request.goal} motivation tips", max_results=3)

    youtube_raw = search_youtube(f"{request.goal} motivation fitness")[:3]
    youtube_videos = [{"title": v.split(" - ")[0], "url": v.split(" - ")[1]} for v in youtube_raw]

    return MotivationResponse(
        prompt=motivation_text,
        web_results=web_results,
        youtube_videos=youtube_videos
    )
