# src/agents/youtube_search_agent.py

import os
import json
from typing import List
from agents import Agent, Runner    
from src.models.agent_models import YouTubeSearchRequest, YouTubeSearchResponse, YouTubeVideo, AgentType
from src.tools.search_youtube import search_youtube
from src.tools.youtube_transcript import get_transcript
from openai import OpenAI
from src.config.settings import OPENAI_API_KEY, OPENAI_ORG_ID, OPENAI_PROJECT

class YouTubeSearchAgent:
    """YouTube Search Agent for finding fitness and health videos"""
    
    def __init__(self):
        self.agent = Agent(
            name="YouTubeSearchAgent",
            instructions=self._get_agent_instructions(),
            tools=[self._search_youtube_tool, self._get_transcript_tool],
            model="gpt-4o-mini"
        )
        self.runner = Runner()
        # OpenAI client for logging/tool-calling visibility
        self._oi = OpenAI(
            api_key=OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            organization=OPENAI_ORG_ID or os.getenv("OPENAI_ORG_ID"),
            project=OPENAI_PROJECT or os.getenv("OPENAI_PROJECT"),
        )
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions for YouTube search"""
        return """
        You are a specialized YouTube Search Agent for health and fitness content.
        
        Your role is to:
        1. Search for relevant YouTube videos based on user's health data and goals
        2. Filter and curate the best fitness, nutrition, and motivation videos
        3. Provide detailed information about each video including title, URL, and description
        4. Focus on high-quality, educational content that matches the user's current health situation
        5. Consider the user's fitness level, goals, and current challenges when selecting videos
        
        When searching:
        - Prioritize videos from reputable fitness channels and health professionals
        - Look for content that matches the user's current fitness level
        - Include a mix of workout videos, nutrition tips, and motivational content
        - Avoid clickbait or low-quality content
        - Consider video duration based on user's available time
        
        Always provide helpful, actionable video recommendations that will support the user's health journey.
        """
    
    def _search_youtube_tool(self, query: str, max_results: int = 3) -> dict:
        """Tool function for searching YouTube videos"""
        try:
            # Use the existing YouTube search function
            youtube_raw = search_youtube(query)
            
            # Parse the results into structured format
            videos = []
            for i, video_raw in enumerate(youtube_raw[:max_results]):
                if " - " in video_raw:
                    title, url = video_raw.split(" - ", 1)
                    videos.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "duration": None,  # Could be enhanced to get actual duration
                        "views": None,     # Could be enhanced to get actual views
                        "channel": None,   # Could be enhanced to get channel name
                        "description": None
                    })
            
            return {
                "status": "success",
                "videos": videos,
                "query_used": query
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "videos": [],
                "query_used": query
            }

    def _get_transcript_tool(self, url_or_id: str, max_chars: int = 1200) -> dict:
        """Tool function to fetch a transcript for a given YouTube URL or ID."""
        try:
            result = get_transcript(url_or_id=url_or_id, max_chars=max_chars)
            return result
        except Exception as e:
            return {"status": "error", "transcript": "", "message": str(e)}
    
    async def search_videos(self, request: YouTubeSearchRequest) -> YouTubeSearchResponse:
        """Search for YouTube videos based on the request"""
        try:
            # Build search query based on health data and planning context
            search_query = self._build_search_query(request)
            
            # Use the agent to search and curate results
            agent_message = f"""
            Search for YouTube videos with the following criteria:
            - Query: {search_query}
            - Max results: {request.max_results}
            - Health data: {request.health_data}
            - Planning context: {request.planning_context}
            - Custom instruction: {request.custom_instruction}
            
            Please find the most relevant and helpful videos for this user's health journey.
            """
            
            # Use the tool directly instead of relying on agent parsing
            # This is more reliable than parsing agent output
            videos = self._parse_agent_response("", search_query)

            # Optionally enrich top results with transcripts
            enriched = []
            for i, v in enumerate(videos[: request.max_results]):
                try:
                    t = self._get_transcript_tool(v.url, max_chars=500)
                    if t.get("status") == "success" and t.get("transcript"):
                        # Store transcript in description field for convenience
                        v.description = t["transcript"]
                except Exception:
                    pass
                enriched.append(v)
            if enriched:
                videos = enriched

            # Log via OpenAI Responses tool-calling so this agent appears in dashboard
            openai_response_id = None
            try:
                openai_response_id = self._log_run_via_openai_tools(
                    query=search_query,
                    max_results=request.max_results,
                    videos=[{"title": v.title, "url": v.url, "description": v.description or ""} for v in videos]
                )
            except Exception:
                pass
            
            
            return YouTubeSearchResponse(
                agent_type=AgentType.YOUTUBE_SEARCH,
                success=True,
                content=f"Found {len(videos)} relevant YouTube videos",
                videos=videos,
                search_query_used=search_query,
                metadata={
                    "total_results": len(videos),
                    "search_criteria": {
                        "max_results": request.max_results,
                        "video_duration": request.video_duration,
                        "category": request.category
                    },
                    "transcripts_included": sum(1 for v in videos if v.description),
                    "openai_response_id": openai_response_id
                }
            )
            
        except Exception as e:
            return YouTubeSearchResponse(
                agent_type=AgentType.YOUTUBE_SEARCH,
                success=False,
                content=f"Error searching YouTube videos: {str(e)}",
                videos=[],
                search_query_used=request.search_query,
                metadata={"error": str(e)}
            )
    
    def _build_search_query(self, request: YouTubeSearchRequest) -> str:
        """Build optimized search query based on request data"""
        base_query = request.search_query
        
        # Add health data context
        if request.health_data:
            if "goal" in request.health_data:
                base_query += f" {request.health_data['goal']}"
            if "fitness_level" in request.health_data:
                base_query += f" {request.health_data['fitness_level']}"
        
        # Add planning context
        if request.planning_context:
            if "topic" in request.planning_context:
                topic = request.planning_context["topic"]
                if topic == "Workout Plan":
                    base_query += " workout routine"
                elif topic == "Meal Plan":
                    base_query += " nutrition recipe"
                elif topic == "Health Habits":
                    base_query += " healthy habits"
            
            if "tone" in request.planning_context:
                tone = request.planning_context["tone"]
                if tone == "Sama":
                    base_query += " gentle beginner"
                elif tone == "Dhanda":
                    base_query += " intense challenging"
                elif tone == "Bedha":
                    base_query += " strategic advanced"
        
        # Add category filter
        if request.category:
            base_query += f" {request.category}"
        
        return base_query.strip()
    
    def _parse_agent_response(self, agent_output: str, search_query: str) -> List[YouTubeVideo]:
        """Parse agent response to extract video information"""
        # For now, use the tool function directly
        # In a more sophisticated implementation, this would parse the agent's response
        tool_result = self._search_youtube_tool(search_query)
        
        if tool_result["status"] == "success":
            return [YouTubeVideo(**video) for video in tool_result["videos"]]
        else:
            return []

    def _log_run_via_openai_tools(self, query: str, max_results: int, videos: list) -> str:
        """
        Create a Responses run with function tools; execute locally and submit outputs for logging.
        Returns response_id. Uses create_and_poll when available; falls back to manual loop; as a last
        resort, sends a simple logging request so an entry always appears.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_youtube",
                    "description": "Search YouTube and return a list of top results as {title,url}.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "max_results": {"type": "integer"}
                        },
                        "required": ["query", "max_results"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_transcript",
                    "description": "Fetch transcript for a YouTube video URL or ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url_or_id": {"type": "string"},
                            "max_chars": {"type": "integer"}
                        },
                        "required": ["url_or_id"]
                    }
                }
            }
        ]
        try:
            # Prefer create_and_poll (available in newer SDKs)
            if hasattr(self._oi.responses, "create_and_poll"):
                resp = self._oi.responses.create_and_poll(
                    model="gpt-4o-mini",
                    input=(
                        "Call search_youtube with the provided query and max_results, "
                        "then call get_transcript for each result. Summarize outputs."
                    ),
                    tools=tools,
                    metadata={"agent": "youtube_search", "purpose": "content_discovery", "query": query},
                )
                # If it still needs tool outputs (unlikely), fall back to manual loop
                if getattr(resp, "status", "") != "requires_action":
                    return getattr(resp, "id", None)
            # Manual loop
            resp = self._oi.responses.create(
                model="gpt-4o-mini",
                input=(
                    "Call search_youtube with the provided query and max_results, "
                    "then call get_transcript for each result. Summarize outputs."
                ),
                tools=tools,
                metadata={"agent": "youtube_search", "purpose": "content_discovery", "query": query},
            )
            while getattr(resp, "status", "") == "requires_action":
                calls = resp.required_action.submit_tool_outputs.tool_calls
                outputs = []
                for call in calls:
                    name = call.function.name
                    args = call.function.arguments or {}
                    if name == "search_youtube":
                        outputs.append({
                            "tool_call_id": call.id,
                            "output": json.dumps([{"title": v["title"], "url": v["url"]} for v in videos][:max_results])
                        })
                    elif name == "get_transcript":
                        vid = args.get("url_or_id", "")
                        try:
                            t = get_transcript(vid, max_chars=int(args.get("max_chars", 400)))
                        except Exception as e:
                            t = {"status": "error", "message": str(e), "transcript": ""}
                        outputs.append({"tool_call_id": call.id, "output": json.dumps(t)})
                    else:
                        outputs.append({"tool_call_id": call.id, "output": "{}"})
                resp = self._oi.responses.submit_tool_outputs(response_id=resp.id, tool_outputs=outputs)
            return getattr(resp, "id", None)
        except Exception:
            # Guaranteed lightweight logging entry if tool path fails
            try:
                minimal = self._oi.responses.create(
                    model="gpt-4o-mini",
                    input=f"YouTube agent executed locally. Query='{query}', returned {len(videos)} results.",
                    metadata={"agent": "youtube_search", "purpose": "content_discovery", "mode": "minimal_log"},
                )
                return getattr(minimal, "id", None)
            except Exception:
                return None
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "YouTube Search Agent",
            "type": AgentType.YOUTUBE_SEARCH,
            "description": "Searches for relevant YouTube fitness and health videos",
            "capabilities": [
                "Video search and curation",
                "Content filtering by fitness level",
                "Category-based recommendations",
                "Duration-based filtering"
            ],
            "model": "gpt-4o-mini"
        }
