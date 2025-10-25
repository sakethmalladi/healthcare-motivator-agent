# src/agents/health_coordinator.py

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from src.agents.youtube_search_agent import YouTubeSearchAgent
from src.agents.curated_search_agent import CuratedSearchAgent
from src.agents.web_search_agent import WebSearchAgent
from src.agents.journaling_agent import JournalingAgent
from src.agents.planning_agent import PlanningAgent
from src.models.agent_models import (
    CoordinatedResponse, PlanningRequest, YouTubeSearchRequest, 
    CuratedSearchRequest, WebSearchRequest, JournalingRequest,
    AgentType
)
from src.models.health_kit_models import HealthKitData
from src.utils.prompt_builder import build_agent_specific_prompt

class HealthCoordinator:
    """Main coordinator that manages all 4 agents in parallel"""
    
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.youtube_agent = YouTubeSearchAgent()
        self.curated_agent = CuratedSearchAgent()
        self.web_agent = WebSearchAgent()
        self.journaling_agent = JournalingAgent()
    
    async def process_health_request(self, user_id: str, health_data: Dict[str, Any], 
                                   custom_instruction: str = None) -> CoordinatedResponse:
        """Process a health request using all agents in parallel"""
        try:
            # Step 1: Create planning request
            planning_request = PlanningRequest(
                user_id=user_id,
                health_data=health_data,
                user_goals=health_data.get("goals", []),
                user_preferences=health_data.get("preferences", {}),
                custom_instruction=custom_instruction,
                health_analysis=health_data  # Pass the health_data as health_analysis
            )
            
            # Step 2: Get planning decision (this runs first as other agents depend on it)
            planning_response = await self.planning_agent.create_plan(planning_request)
            
            if not planning_response.success:
                return CoordinatedResponse(
                    user_id=user_id,
                    planning_decision=planning_response.decision,
                    overall_summary="Planning failed, unable to coordinate other agents",
                    metadata={"error": "Planning agent failed"}
                )
            
            # Step 3: Create requests for all other agents based on planning decision
            planning_context = planning_response.context_for_other_agents
            
            # Create agent requests with enhanced search queries
            youtube_request = YouTubeSearchRequest(
                user_id=user_id,
                health_data=health_data,
                planning_context=planning_context,
                custom_instruction=custom_instruction,
                search_query=self._build_enhanced_search_query(health_data, planning_response.decision, "fitness"),
                max_results=3,
                category="fitness"
            )
            
            curated_request = CuratedSearchRequest(
                user_id=user_id,
                health_data=health_data,
                planning_context=planning_context,
                custom_instruction=custom_instruction,
                search_query=self._build_enhanced_search_query(health_data, planning_response.decision, "health"),
                max_results=3,
                content_type="article"
            )
            
            web_request = WebSearchRequest(
                user_id=user_id,
                health_data=health_data,
                planning_context=planning_context,
                custom_instruction=custom_instruction,
                search_query=self._build_enhanced_search_query(health_data, planning_response.decision, "health community"),
                max_results=3,
                search_type="general"
            )
            
            journaling_request = JournalingRequest(
                user_id=user_id,
                health_data=health_data,
                planning_context=planning_context,
                custom_instruction=custom_instruction,
                journal_type=self._determine_journal_type(planning_context),
                mood=health_data.get("mood"),
                energy_level=health_data.get("energy_level"),
                challenges_faced=health_data.get("challenges", []),
                achievements=health_data.get("achievements", [])
            )
            
            # Step 4: Run all agents in parallel
            youtube_task = self.youtube_agent.search_videos(youtube_request)
            curated_task = self.curated_agent.search_articles(curated_request)
            web_task = self.web_agent.search_web(web_request)
            journaling_task = self.journaling_agent.create_journal_entry(journaling_request)
            
            # Wait for all agents to complete
            youtube_response, curated_response, web_response, journaling_response = await asyncio.gather(
                youtube_task, curated_task, web_task, journaling_task,
                return_exceptions=True
            )
            
            # Step 5: Handle any exceptions
            if isinstance(youtube_response, Exception):
                youtube_response = None
            if isinstance(curated_response, Exception):
                curated_response = None
            if isinstance(web_response, Exception):
                web_response = None
            if isinstance(journaling_response, Exception):
                journaling_response = None
            
            # Step 6: Create coordinated response
            overall_summary = self._create_overall_summary(
                planning_response, youtube_response, curated_response, 
                web_response, journaling_response
            )
            
            return CoordinatedResponse(
                user_id=user_id,
                planning_decision=planning_response.decision,
                youtube_results=youtube_response,
                curated_results=curated_response,
                web_results=web_response,
                journaling_results=journaling_response,
                overall_summary=overall_summary,
                metadata={
                    "agents_successful": sum([
                        1 for response in [youtube_response, curated_response, web_response, journaling_response]
                        if response and response.success
                    ]),
                    "total_agents": 4,
                    "planning_confidence": planning_response.decision.confidence_score
                }
            )
            
        except Exception as e:
            # Create a default planning decision for error cases
            from src.models.agent_models import PlanningDecision
            default_decision = PlanningDecision(
                theme="Crisis Intervention",
                topic="Health Habits",
                tone="Sama",
                tone_description="Gentle, peaceful approach",
                tone_characteristics=["compassionate", "balanced"],
                timing={"immediate": True, "frequency": "daily"},
                reasoning=f"Error fallback: {str(e)}",
                confidence_score=0.1
            )
            
            return CoordinatedResponse(
                user_id=user_id,
                planning_decision=default_decision,
                overall_summary=f"Error processing health request: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _build_search_query(self, base_query: str, planning_context: Dict[str, Any]) -> str:
        """Build search query based on planning context using enhanced prompt builder"""
        query_parts = [base_query]
        
        if planning_context:
            if "topic" in planning_context:
                topic = planning_context["topic"]
                if topic == "Workout Plan":
                    query_parts.append("workout exercise fitness")
                elif topic == "Meal Plan":
                    query_parts.append("nutrition diet meal planning")
                elif topic == "Health Habits":
                    query_parts.append("healthy habits lifestyle")
            
            if "tone" in planning_context:
                tone = planning_context["tone"]
                if tone == "Sama":
                    query_parts.append("gentle beginner")
                elif tone == "Dhanda":
                    query_parts.append("intense challenging")
                elif tone == "Bedha":
                    query_parts.append("strategic advanced")
        
        return " ".join(query_parts)
    
    def _build_enhanced_search_query(self, health_data: Dict[str, Any], planning_decision, query_type: str) -> str:
        """Build enhanced search query using prompt builder"""
        # Create a mock planning decision if not available
        if not hasattr(planning_decision, 'topic'):
            return self._build_search_query(f"{query_type} health", {"topic": "Health Habits"})
        
        # Use the enhanced prompt builder for context-aware queries
        base_query = f"{query_type} {planning_decision.topic.lower()}"
        
        # Add tone-specific modifiers
        if planning_decision.tone == "Sama":
            base_query += " gentle beginner"
        elif planning_decision.tone == "Dhanda":
            base_query += " intense challenging"
        elif planning_decision.tone == "Bedha":
            base_query += " strategic advanced"
        
        return base_query
    
    def _determine_journal_type(self, planning_context: Dict[str, Any]) -> str:
        """Determine journal type based on planning context"""
        if not planning_context:
            return "daily_reflection"
        
        theme = planning_context.get("theme", "")
        
        if "crisis" in theme.lower():
            return "struggle_support"
        elif "progress" in theme.lower() or "celebration" in theme.lower():
            return "progress_update"
        elif "goal" in theme.lower():
            return "goal_setting"
        else:
            return "daily_reflection"
    
    def _create_overall_summary(self, planning_response, youtube_response, 
                               curated_response, web_response, journaling_response) -> str:
        """Create overall summary of all agent responses"""
        summary_parts = []
        
        # Planning summary
        if planning_response and planning_response.success:
            summary_parts.append(f"Planning: {planning_response.decision.tone} approach for {planning_response.decision.topic}")
        
        # Content summary
        content_count = 0
        if youtube_response and youtube_response.success:
            content_count += len(youtube_response.videos)
        if curated_response and curated_response.success:
            content_count += len(curated_response.articles)
        if web_response and web_response.success:
            content_count += len(web_response.results)
        
        if content_count > 0:
            summary_parts.append(f"Found {content_count} relevant resources")
        
        # Journaling summary
        if journaling_response and journaling_response.success:
            summary_parts.append("Created personalized journal entry")
        
        # Success rate
        successful_agents = sum([
            1 for response in [youtube_response, curated_response, web_response, journaling_response]
            if response and response.success
        ])
        summary_parts.append(f"{successful_agents}/4 agents completed successfully")
        
        return " | ".join(summary_parts) if summary_parts else "Health request processed"
    
    def get_coordinator_info(self) -> Dict[str, Any]:
        """Get information about the coordinator and all agents"""
        return {
            "coordinator": {
                "name": "Health Coordinator",
                "description": "Coordinates all health agents in parallel",
                "capabilities": [
                    "Parallel agent execution",
                    "Planning-based coordination",
                    "Response aggregation",
                    "Error handling"
                ]
            },
            "agents": {
                "planning": self.planning_agent.get_agent_info(),
                "youtube": self.youtube_agent.get_agent_info(),
                "curated": self.curated_agent.get_agent_info(),
                "web": self.web_agent.get_agent_info(),
                "journaling": self.journaling_agent.get_agent_info()
            }
        }

