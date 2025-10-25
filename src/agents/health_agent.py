# src/agents/health_agent.py

import os
from openai import OpenAI
from agents import Agent, Runner  # Correct import
from src.models.health_models import MotivationRequest, MotivationResponse
from src.tools.search_web import search_web
from src.tools.search_youtube import search_youtube
from src.utils.prompt_builder import build_prompt, build_system_prompt, build_user_message, build_search_query

def get_client():
    """Create OpenAI client - keeping your existing pattern."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_agents_client():
    """Create OpenAI Agents client."""
    return Runner()

def search_web_function(query: str, max_results: int = 3):
    """Tool function for Agents SDK - wraps your existing search_web."""
    try:
        results = search_web(query, max_results)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_youtube_function(query: str):
    """Tool function for Agents SDK - wraps your existing search_youtube."""
    try:
        youtube_raw = search_youtube(query)[:3]
        youtube_videos = [{"title": v.split(" - ")[0], "url": v.split(" - ")[1]} for v in youtube_raw]
        return {"status": "success", "results": youtube_videos}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Create the agent using the centralized prompt builder
health_motivator_agent = Agent(
    name="HealthMotivator",
    instructions=build_system_prompt(),
    tools=[search_web_function, search_youtube_function],  # Changed from 'functions' to 'tools'
    model="gpt-4o-mini"
)

async def run_health_agent(request: MotivationRequest) -> MotivationResponse:
    """Run the health agent - keeping your exact function signature and logic."""
    
    # Try Agents SDK first, fallback to your existing OpenAI client
    try:
        runner = get_agents_client()
        
        # Use the centralized user message builder for Agents SDK
        user_message = build_user_message(
            previous_data=request.previous_data,
            current_data=request.current_data,
            action_taken=request.action_taken,
            next_action=request.next_action,
            custom_instruction=request.custom_instruction,
            goal=request.goal,
            progress=request.progress
        )
        
        response = runner.run_sync(health_motivator_agent, user_message)
        motivation_text = response.final_output
        
    except Exception as e:
        # Fallback to your existing OpenAI implementation using centralized prompt builder
        print(f"Agents SDK failed, using fallback: {e}")
        client = get_client()
        
        # Use your existing build_prompt function from utils
        prompt = build_prompt(
            previous_data=request.previous_data,
            current_data=request.current_data,
            action_taken=request.action_taken,
            next_action=request.next_action,
            custom_instruction=request.custom_instruction,
            goal=request.goal,
            progress=request.progress
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Motivate me today based on my health data."}
            ]
        )
        motivation_text = response.choices[0].message.content

    # Fallback if the model returns empty - keeping your existing logic
    if not motivation_text or motivation_text.strip() == "":
        motivation_text = f"Great job! You're making progress towards your goal: {request.goal}. Keep it up!"

    # Get top 3 web and YouTube results using centralized search query builder
    web_query = build_search_query(request.goal, "motivation")
    web_results = search_web(web_query, max_results=3)

    youtube_query = build_search_query(request.goal, "fitness")
    youtube_raw = search_youtube(youtube_query)[:3]
    youtube_videos = [{"title": v.split(" - ")[0], "url": v.split(" - ")[1]} for v in youtube_raw]

    return MotivationResponse(
        prompt=motivation_text,
        web_results=web_results,
        youtube_videos=youtube_videos
    )
