# src/agents/curated_search_agent.py

import os
from typing import List
from agents import Agent, Runner
from src.models.agent_models import CuratedSearchRequest, CuratedSearchResponse, CuratedArticle, AgentType
from src.tools.search_web import search_web

class CuratedSearchAgent:
    """Curated Search Agent for finding high-quality health articles and resources"""
    
    def __init__(self):
        self.agent = Agent(
            name="CuratedSearchAgent",
            instructions=self._get_agent_instructions(),
            tools=[self._search_curated_tool],
            model="gpt-4o-mini"
        )
        self.runner = Runner()
        
        # Curated sources for high-quality health content
        self.trusted_sources = [
            "mayoclinic.org",
            "webmd.com",
            "healthline.com",
            "medicalnewstoday.com",
            "pubmed.ncbi.nlm.nih.gov",
            "nutrition.org",
            "acsm.org",
            "acefitness.org",
            "nasm.org",
            "precisionnutrition.com"
        ]
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions for curated search"""
        return """
        You are a specialized Curated Search Agent for high-quality health and fitness content.
        
        Your role is to:
        1. Search for authoritative, evidence-based health articles and resources
        2. Filter content from trusted medical and fitness sources
        3. Prioritize content from reputable institutions and professionals
        4. Focus on educational, research-backed information
        5. Avoid commercial, promotional, or unverified content
        
        When searching:
        - Prioritize content from medical institutions, universities, and professional organizations
        - Look for peer-reviewed studies and evidence-based information
        - Include content from certified nutritionists, dietitians, and fitness professionals
        - Focus on educational value rather than entertainment
        - Consider the user's health goals and current situation
        - Provide accurate, actionable information that supports health decisions
        
        Always ensure the content is from reliable sources and provides genuine value to the user's health journey.
        """
    
    def _search_curated_tool(self, query: str, max_results: int = 3) -> dict:
        """Tool function for searching curated health content"""
        try:
            # Use the existing web search function
            web_results = search_web(query, max_results * 2)  # Get more results to filter
            
            # Filter results to only include trusted sources
            curated_results = []
            for result in web_results:
                if any(source in result.get("url", "").lower() for source in self.trusted_sources):
                    curated_results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "source": self._extract_source_domain(result.get("url", "")),
                        "author": None,  # Could be enhanced to extract author
                        "publish_date": None,  # Could be enhanced to extract date
                        "summary": None,  # Could be enhanced to extract summary
                        "content_type": "article",
                        "difficulty_level": "intermediate"
                    })
                    
                    if len(curated_results) >= max_results:
                        break
            
            return {
                "status": "success",
                "articles": curated_results,
                "query_used": query
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "articles": [],
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
    
    async def search_articles(self, request: CuratedSearchRequest) -> CuratedSearchResponse:
        """Search for curated health articles based on the request"""
        try:
            # Build search query based on health data and planning context
            search_query = self._build_search_query(request)
            
            # Use the agent to search and curate results
            agent_message = f"""
            Search for high-quality health articles with the following criteria:
            - Query: {search_query}
            - Max results: {request.max_results}
            - Content type: {request.content_type}
            - Difficulty level: {request.difficulty_level}
            - Health data: {request.health_data}
            - Planning context: {request.planning_context}
            - Custom instruction: {request.custom_instruction}
            
            Please find the most authoritative and helpful articles for this user's health journey.
            Focus on evidence-based content from trusted sources.
            """
            
            # Run the agent
            response = self.runner.run_sync(self.agent, agent_message)
            
            # Parse the response and extract article information
            articles = self._parse_agent_response(response.final_output, search_query)
            
            return CuratedSearchResponse(
                agent_type=AgentType.CURATED_SEARCH,
                success=True,
                content=f"Found {len(articles)} curated health articles",
                articles=articles,
                search_query_used=search_query,
                metadata={
                    "total_results": len(articles),
                    "trusted_sources_used": len(set(article.source for article in articles)),
                    "search_criteria": {
                        "max_results": request.max_results,
                        "content_type": request.content_type,
                        "difficulty_level": request.difficulty_level
                    }
                }
            )
            
        except Exception as e:
            return CuratedSearchResponse(
                agent_type=AgentType.CURATED_SEARCH,
                success=False,
                content=f"Error searching curated articles: {str(e)}",
                articles=[],
                search_query_used=request.search_query,
                metadata={"error": str(e)}
            )
    
    def _build_search_query(self, request: CuratedSearchRequest) -> str:
        """Build optimized search query based on request data"""
        base_query = request.search_query
        
        # Add health data context
        if request.health_data:
            if "goal" in request.health_data:
                base_query += f" {request.health_data['goal']}"
            if "health_condition" in request.health_data:
                base_query += f" {request.health_data['health_condition']}"
        
        # Add planning context
        if request.planning_context:
            if "topic" in request.planning_context:
                topic = request.planning_context["topic"]
                if topic == "Workout Plan":
                    base_query += " exercise routine fitness"
                elif topic == "Meal Plan":
                    base_query += " nutrition diet meal planning"
                elif topic == "Health Habits":
                    base_query += " healthy lifestyle habits"
            
            if "tone" in request.planning_context:
                tone = request.planning_context["tone"]
                if tone == "Sama":
                    base_query += " gentle approach beginner"
                elif tone == "Dhanda":
                    base_query += " intensive advanced"
                elif tone == "Bedha":
                    base_query += " strategic planning"
        
        # Add content type filter
        if request.content_type:
            if request.content_type == "study":
                base_query += " research study"
            elif request.content_type == "guide":
                base_query += " guide tutorial"
            elif request.content_type == "recipe":
                base_query += " recipe"
        
        # Add difficulty level
        if request.difficulty_level:
            if request.difficulty_level == "beginner":
                base_query += " beginner basics"
            elif request.difficulty_level == "advanced":
                base_query += " advanced expert"
        
        return base_query.strip()
    
    def _parse_agent_response(self, agent_output: str, search_query: str) -> List[CuratedArticle]:
        """Parse agent response to extract article information"""
        # For now, use the tool function directly
        # In a more sophisticated implementation, this would parse the agent's response
        tool_result = self._search_curated_tool(search_query)
        
        if tool_result["status"] == "success":
            return [CuratedArticle(**article) for article in tool_result["articles"]]
        else:
            return []
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Curated Search Agent",
            "type": AgentType.CURATED_SEARCH,
            "description": "Searches for high-quality, evidence-based health articles",
            "capabilities": [
                "Trusted source filtering",
                "Evidence-based content curation",
                "Medical and fitness professional content",
                "Educational resource recommendations"
            ],
            "trusted_sources": self.trusted_sources,
            "model": "gpt-4o-mini"
        }
