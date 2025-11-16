# src/agents/web_search_agent.py

import os
from typing import List
from agents import Agent, Runner
from src.models.agent_models import WebSearchRequest, WebSearchResponse, WebResult, AgentType
from src.tools.search_web import search_web
from openai import OpenAI
from src.config.settings import OPENAI_API_KEY, OPENAI_ORG_ID, OPENAI_PROJECT

class WebSearchAgent:
    """Web Search Agent for general health information and community content"""
    
    def __init__(self):
        self.agent = Agent(
            name="WebSearchAgent",
            instructions=self._get_agent_instructions(),
            tools=[self._search_web_tool],
            model="gpt-4o-mini"
        )
        self.runner = Runner()
        # OpenAI client for request logging/observability
        self._oi = OpenAI(
            api_key=OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            organization=OPENAI_ORG_ID or os.getenv("OPENAI_ORG_ID"),
            project=OPENAI_PROJECT or os.getenv("OPENAI_PROJECT")
        )
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions for web search"""
        return """
        You are a specialized Web Search Agent for health and fitness information.
        
        Your role is to:
        1. Search for general health information, news, and community content
        2. Find diverse perspectives and real-world experiences
        3. Include forum discussions, blog posts, and community insights
        4. Provide a broad view of health topics and trends
        5. Complement curated content with general web information
        
        When searching:
        - Look for recent news and trends in health and fitness
        - Include community discussions and personal experiences
        - Find practical tips and real-world advice
        - Consider different perspectives and approaches
        - Include both professional and community content
        - Focus on actionable, practical information
        
        Always provide a balanced view of health information from various sources and communities.
        """
    
    def _search_web_tool(self, query: str, max_results: int = 3) -> dict:
        """Tool function for searching the web"""
        try:
            # Use the existing web search function
            web_results = search_web(query, max_results)
            
            # Convert to structured format
            results = []
            for result in web_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": None,  # Could be enhanced to extract snippet
                    "source": self._extract_source_domain(result.get("url", "")),
                    "publish_date": None  # Could be enhanced to extract date
                })
            
            return {
                "status": "success",
                "results": results,
                "query_used": query
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "results": [],
                "query_used": query
            }
    
    def _extract_source_domain(self, url: str) -> str:
        """Extract the main domain from a URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return "unknown"
    
    async def search_web(self, request: WebSearchRequest) -> WebSearchResponse:
        """Search the web for health information based on the request"""
        try:
            # Build search query based on health data and planning context
            search_query = self._build_search_query(request)
            
            # Use the agent to search and analyze results
            agent_message = f"""
            Search the web for health information with the following criteria:
            - Query: {search_query}
            - Max results: {request.max_results}
            - Search type: {request.search_type}
            - Health data: {request.health_data}
            - Planning context: {request.planning_context}
            - Custom instruction: {request.custom_instruction}
            
            Please find diverse, practical health information that complements other sources.
            Include community insights, recent trends, and real-world experiences.
            """
            
            # Use the tool directly instead of relying on agent parsing
            # This is more reliable than parsing agent output
            results = self._parse_agent_response("", search_query)

            # Log via OpenAI for observability
            openai_response_id = None
            try:
                if hasattr(self._oi.responses, "create_and_poll"):
                    resp = self._oi.responses.create_and_poll(
                        model="gpt-4o-mini",
                        input=f"Web search executed. Query='{search_query}', returned {len(results)} results.",
                        metadata={"agent": "web_search", "purpose": "content_discovery", "query": search_query}
                    )
                else:
                    resp = self._oi.responses.create(
                        model="gpt-4o-mini",
                        input=f"Web search executed. Query='{search_query}', returned {len(results)} results.",
                        metadata={"agent": "web_search", "purpose": "content_discovery", "query": search_query}
                    )
                openai_response_id = getattr(resp, "id", None)
            except Exception:
                pass
            
            return WebSearchResponse(
                agent_type=AgentType.WEB_SEARCH,
                success=True,
                content=f"Found {len(results)} web results",
                results=results,
                search_query_used=search_query,
                metadata={
                    "total_results": len(results),
                    "search_criteria": {
                        "max_results": request.max_results,
                        "search_type": request.search_type
                    },
                    "openai_response_id": openai_response_id
                }
            )
            
        except Exception as e:
            return WebSearchResponse(
                agent_type=AgentType.WEB_SEARCH,
                success=False,
                content=f"Error searching web: {str(e)}",
                results=[],
                search_query_used=request.search_query,
                metadata={"error": str(e)}
            )
    
    def _build_search_query(self, request: WebSearchRequest) -> str:
        """Build optimized search query based on request data"""
        base_query = request.search_query
        
        # Add health data context
        if request.health_data:
            if "goal" in request.health_data:
                base_query += f" {request.health_data['goal']}"
            if "challenge" in request.health_data:
                base_query += f" {request.health_data['challenge']}"
        
        # Add planning context
        if request.planning_context:
            if "topic" in request.planning_context:
                topic = request.planning_context["topic"]
                if topic == "Workout Plan":
                    base_query += " fitness workout community"
                elif topic == "Meal Plan":
                    base_query += " nutrition diet community"
                elif topic == "Health Habits":
                    base_query += " healthy lifestyle community"
            
            if "tone" in request.planning_context:
                tone = request.planning_context["tone"]
                if tone == "Sama":
                    base_query += " gentle approach community"
                elif tone == "Dhanda":
                    base_query += " intense challenging community"
                elif tone == "Bedha":
                    base_query += " strategic planning community"
        
        # Add search type modifier
        if request.search_type:
            if request.search_type == "news":
                base_query += " news latest"
            elif request.search_type == "academic":
                base_query += " research study"
            elif request.search_type == "forum":
                base_query += " forum discussion community"
        
        return base_query.strip()
    
    def _parse_agent_response(self, agent_output: str, search_query: str) -> List[WebResult]:
        """Parse agent response to extract web results"""
        # For now, use the tool function directly
        # In a more sophisticated implementation, this would parse the agent's response
        tool_result = self._search_web_tool(search_query)
        
        if tool_result["status"] == "success":
            return [WebResult(**result) for result in tool_result["results"]]
        else:
            return []
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Web Search Agent",
            "type": AgentType.WEB_SEARCH,
            "description": "Searches for general health information and community content",
            "capabilities": [
                "General web search",
                "Community content discovery",
                "News and trend analysis",
                "Diverse perspective gathering"
            ],
            "model": "gpt-4o-mini"
        }
