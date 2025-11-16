# src/agents/planning_agent.py

import os
import json
from typing import Dict, Any
from openai import OpenAI
from agents import Agent, Runner
from src.config.settings import OPENAI_API_KEY, OPENAI_ORG_ID, OPENAI_PROJECT, PLANNING_MODEL, OPENAI_TEMPERATURE
from src.models.agent_models import (
    PlanningRequest, PlanningResponse, PlanningDecision, AgentType,
    WebSearchRequest, YouTubeSearchRequest, CuratedSearchRequest
)
from src.models.health_kit_models import HealthAnalysis
from src.tools.planning_tool import PlanningTool, IndianTone, HealthTopic, HealthTheme
from src.utils.prompt_builder import build_planning_prompt
from src.agents.web_search_agent import WebSearchAgent
from src.agents.youtube_search_agent import YouTubeSearchAgent
from src.agents.curated_search_agent import CuratedSearchAgent
from src.tools.health_analysis_tool import analyze_health_score

class PlanningAgent:
    """AI Planning Agent for determining theme, topic, tone, and timing"""
    
    def __init__(self):
        # Attach org/project so requests show under the same project in the dashboard
        self.client = OpenAI(
            api_key=OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            organization=OPENAI_ORG_ID or os.getenv("OPENAI_ORG_ID"),
            project=OPENAI_PROJECT or os.getenv("OPENAI_PROJECT")
        )
        self.model = PLANNING_MODEL
        self.planning_tool = PlanningTool()
        self.web_search_agent = WebSearchAgent()
        self.youtube_search_agent = YouTubeSearchAgent()
        self.curated_search_agent = CuratedSearchAgent()
        # Local Agents SDK (same pattern as JournalingAgent)
        self.agent = Agent(
            name="PlanningAgent",
            instructions=self._get_agent_instructions(),
            tools=[analyze_health_score],  # expose analysis tool to the agent
            model=self.model
        )
        self.runner = Runner()
        # OpenAI client for logging visibility
        self._oi = OpenAI(
            api_key=OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
            organization=OPENAI_ORG_ID or os.getenv("OPENAI_ORG_ID"),
            project=OPENAI_PROJECT or os.getenv("OPENAI_PROJECT")
        )

    def _log_planning_run(self, decision: PlanningDecision, user_id: str) -> str:
        """
        Create a minimal OpenAI Responses log entry for the planning decision.
        Always returns a response_id if the call succeeds; None otherwise.
        """
        try:
            summary = json.dumps({
                "theme": decision.theme,
                "topic": decision.topic,
                "tone": decision.tone,
                "timing": decision.timing,
                "confidence": decision.confidence_score,
                "reasoning": decision.reasoning[:400] + ("..." if len(decision.reasoning) > 400 else "")
            }, ensure_ascii=False)

            # Prefer create_and_poll when available
            if hasattr(self._oi.responses, "create_and_poll"):
                resp = self._oi.responses.create_and_poll(
                    model=self.model,
                    input=f"Planning decision (user={user_id}): {summary}",
                    metadata={
                        "agent": "planning_agent",
                        "purpose": "health_planning",
                        "user": user_id
                    },
                )
                return getattr(resp, "id", None)

            # Fallback to simple create
            resp = self._oi.responses.create(
                model=self.model,
                input=f"Planning decision (user={user_id}): {summary}",
                metadata={
                    "agent": "planning_agent",
                    "purpose": "health_planning",
                    "user": user_id
                },
            )
            return getattr(resp, "id", None)
        except Exception:
            return None
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions for planning"""
        return """
        You are a specialized AI Planning Agent for health and fitness guidance.
        
        Your role is to:
        1. Analyze user's health data and determine the appropriate theme
        2. Select the most relevant topic (Workout Plan, Meal Plan, Health Habits)
        3. Choose the appropriate Indian historical tone (Sama, Dana, Dhanda, Bedha)
        4. Determine optimal timing for user engagement
        5. Provide reasoning for all decisions
        
        Indian Historical Context for Tones:
        - Sama (सम): Gentle, peaceful approach like Buddha's middle path - use for beginners, sensitive situations, or when user needs gentle support
        - Dana (दान): Generous, giving approach like a wise teacher - use for progress celebration, learning moments, or habit building
        - Dhanda (दंड): Firm, disciplinary approach like a strict guru - use when user lacks progress, makes excuses, or needs discipline
        - Bedha (भेद): Strategic, analytical approach like Chanakya's tactics - use for complex goals, plateau situations, or optimization needs
        
        Topics:
        - Workout Plan: Focus on exercise routines, fitness activities, physical training
        - Meal Plan: Focus on nutrition, diet planning, healthy eating habits
        - Health Habits: Focus on lifestyle changes, daily routines, wellness practices
        
        Themes:
        - Motivation Needed: User needs encouragement and motivation
        - Progress Celebration: User has made good progress and should be celebrated
        - Struggle Support: User is struggling and needs emotional support
        - Goal Adjustment: User's goals need to be modified or refined
        - Habit Building: User needs help building consistent habits
        - Crisis Intervention: User needs immediate support and intervention
        
        Always provide clear reasoning for your decisions and consider the user's current emotional state, progress level, and specific needs.
        """
    
    async def create_plan(self, request: PlanningRequest) -> PlanningResponse:
        """Create a comprehensive health plan based on the request"""
        try:
            # First, analyze health using our tool (deterministic, no network)
            health_analysis_dict = analyze_health_score(request.health_data)
            
            # Use the enhanced prompt builder
            user_message = build_planning_prompt(
                health_data=request.health_data,
                user_goals=request.user_goals,
                user_preferences=request.user_preferences
            )
            # Append health analysis context from tool for stronger grounding
            user_message += f"\n\nHEALTH_ANALYSIS:\n{json.dumps(health_analysis_dict, ensure_ascii=False)}"
            
            # Use local Agents SDK runner (consistent with JournalingAgent)
            agent_response = await self.runner.run(self.agent, user_message)
            response_text = agent_response.final_output.strip() if agent_response and agent_response.final_output else ""
            if not response_text:
                raise ValueError("OpenAI API returned response with only whitespace")
            
            # Parse the LLM response to extract decisions
            # This will raise ValueError or KeyError if parsing fails
            decisions = self._parse_agent_response(response_text)
            
            # Create the planning decision
            # Since _parse_agent_response validates all fields, we can safely access them directly
            planning_decision = PlanningDecision(
                theme=decisions["theme"],
                topic=decisions["topic"],
                tone=decisions["tone"],
                tone_description=self._get_tone_description(decisions["tone"]),
                tone_characteristics=self._get_tone_characteristics(decisions["tone"]),
                timing=decisions["timing"],
                reasoning=decisions["reasoning"],
                confidence_score=decisions["confidence"]
            )
            
            # Create context for other agents
            # Build PlanningDecision context using health_analysis_dict
            context_for_agents = {
                "theme": planning_decision.theme,
                "topic": planning_decision.topic,
                "tone": planning_decision.tone,
                "tone_description": planning_decision.tone_description,
                "tone_characteristics": planning_decision.tone_characteristics,
                "timing": planning_decision.timing,
                "health_score": health_analysis_dict["overall_health_score"],
                "recommendations": health_analysis_dict["recommendations"],
                "concerns": health_analysis_dict["concerns"],
                "achievements": health_analysis_dict["achievements"],
                "next_goals": health_analysis_dict["next_goals"]
            }
            
            # Step 2: Stop here - downstream agents run in coordinator (parallelized)
            # Log planning result to OpenAI for observability (robust helper)
            openai_response_id = self._log_planning_run(planning_decision, request.user_id)

            return PlanningResponse(
                agent_type=AgentType.PLANNING,
                success=True,
                content=f"Created health plan with {planning_decision.tone} tone for {planning_decision.topic}",
                decision=planning_decision,
                context_for_other_agents=context_for_agents,
                metadata={
                    "health_score": health_analysis_dict["overall_health_score"],
                    "confidence": planning_decision.confidence_score,
                    "reasoning": planning_decision.reasoning,
                    "web_search_results": 0,
                    "youtube_search_results": 0,
                    "curated_results": 0,
                    "raw_llm_response": response_text[:2000],
                    "openai_response_id": openai_response_id
                }
            )
            
        except Exception as e:
            # Return a safe default but allow pipeline to proceed
            fallback_decision = PlanningDecision(
                theme="Habit Building",
                topic="Health Habits",
                tone="Sama",
                tone_description="Gentle, peaceful approach",
                tone_characteristics=["compassionate", "balanced"],
                timing={"immediate": False, "frequency": "daily"},
                reasoning=f"Fallback used due to error: {str(e)}",
                confidence_score=0.2
            )
            return PlanningResponse(
                agent_type=AgentType.PLANNING,
                success=True,
                content="Fallback planning decision created",
                decision=fallback_decision,
                context_for_other_agents={
                    "theme": fallback_decision.theme,
                    "topic": fallback_decision.topic,
                    "tone": fallback_decision.tone,
                    "tone_description": fallback_decision.tone_description,
                    "tone_characteristics": fallback_decision.tone_characteristics,
                    "timing": fallback_decision.timing,
                    "health_score": 50.0,
                    "recommendations": [],
                    "concerns": [],
                    "achievements": [],
                    "next_goals": []
                },
                metadata={"error": str(e)}
            )
    
    def _build_planning_context(self, request: PlanningRequest, health_analysis: HealthAnalysis) -> str:
        """Build context for the planning agent"""
        context_parts = []
        
        # Add health score context
        if health_analysis.overall_health_score < 30:
            context_parts.append("CRISIS: Very low health score, needs immediate intervention")
        elif health_analysis.overall_health_score < 50:
            context_parts.append("STRUGGLE: Low health score, needs support and motivation")
        elif health_analysis.overall_health_score < 70:
            context_parts.append("PROGRESS: Moderate health score, needs motivation and guidance")
        elif health_analysis.overall_health_score < 85:
            context_parts.append("GOOD: High health score, focus on habit building")
        else:
            context_parts.append("EXCELLENT: Very high health score, celebrate progress")
        
        # Add concerns context
        if health_analysis.concerns:
            context_parts.append(f"CONCERNS: {', '.join(health_analysis.concerns)}")
        
        # Add achievements context
        if health_analysis.achievements:
            context_parts.append(f"ACHIEVEMENTS: {', '.join(health_analysis.achievements)}")
        
        # Add user goals context
        if request.user_goals:
            context_parts.append(f"USER GOALS: {', '.join(request.user_goals)}")
        
        return " | ".join(context_parts) if context_parts else "General health planning"
    
    def _parse_agent_response(self, agent_output: str) -> Dict[str, Any]:
        """Parse the LLM's JSON response to extract planning decisions
        
        Raises:
            ValueError: If JSON parsing fails or required fields are missing
            KeyError: If required fields are missing from the response
        """
        if not agent_output or not agent_output.strip():
            raise ValueError("LLM response is empty or contains only whitespace")
        
        # Try to extract JSON from the response
        original_output = agent_output
        agent_output = agent_output.strip()
        
        # Remove markdown code blocks if present
        if "```json" in agent_output:
            start = agent_output.find("```json") + 7
            end = agent_output.find("```", start)
            if end != -1:
                agent_output = agent_output[start:end].strip()
        elif "```" in agent_output:
            start = agent_output.find("```") + 3
            end = agent_output.find("```", start)
            if end != -1:
                agent_output = agent_output[start:end].strip()
        
        # Try to find JSON object boundaries
        if "{" not in agent_output or "}" not in agent_output:
            raise ValueError(
                f"LLM response does not contain valid JSON. "
                f"Response (first 200 chars): {original_output[:200]}..."
            )
        
        start = agent_output.find("{")
        end = agent_output.rfind("}") + 1
        agent_output = agent_output[start:end]
        
        # Parse JSON
        try:
            parsed = json.loads(agent_output)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse LLM response as JSON: {str(e)}. "
                f"Response (first 200 chars): {original_output[:200]}..."
            ) from e
        
        # Validate structure
        if not isinstance(parsed, dict):
            raise ValueError(
                f"LLM response is not a valid JSON object. "
                f"Got type: {type(parsed)}. Response: {original_output[:200]}..."
            )
        
        # Required fields
        required_fields = ["theme", "topic", "tone", "timing", "reasoning", "confidence"]
        missing_fields = [field for field in required_fields if field not in parsed]
        if missing_fields:
            raise KeyError(
                f"LLM response is missing required fields: {', '.join(missing_fields)}. "
                f"Response: {json.dumps(parsed, indent=2)}"
            )
        
        # Validate timing structure
        if not isinstance(parsed["timing"], dict):
            raise ValueError(
                f"Timing field must be a dictionary, got: {type(parsed['timing'])}. "
                f"Value: {parsed['timing']}"
            )
        
        timing_required_fields = ["immediate", "frequency"]
        missing_timing_fields = [field for field in timing_required_fields if field not in parsed["timing"]]
        if missing_timing_fields:
            raise KeyError(
                f"Timing object is missing required fields: {', '.join(missing_timing_fields)}. "
                f"Timing object: {json.dumps(parsed['timing'], indent=2)}"
            )
        
        # Validate confidence is a number
        try:
            confidence = float(parsed["confidence"])
            if not (0.0 <= confidence <= 1.0):
                raise ValueError(
                    f"Confidence must be between 0 and 1, got: {confidence}"
                )
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Confidence must be a number between 0 and 1, got: {parsed['confidence']} (type: {type(parsed['confidence'])})"
            ) from e
        
        # Build decisions dict
        decisions = {
            "theme": str(parsed["theme"]),
            "topic": str(parsed["topic"]),
            "tone": str(parsed["tone"]),
            "timing": {
                "immediate": bool(parsed["timing"]["immediate"]),
                "frequency": str(parsed["timing"]["frequency"])
            },
            "reasoning": str(parsed["reasoning"]),
            "confidence": confidence
        }
        
        return decisions
    
    def _build_search_query(self, planning_decision: PlanningDecision, health_analysis: HealthAnalysis, user_goals: list) -> str:
        """Build search query based on planning decision and health analysis"""
        query_parts = []
        
        # Add topic
        if planning_decision.topic == "Workout Plan":
            query_parts.append("workout exercise fitness routine")
        elif planning_decision.topic == "Meal Plan":
            query_parts.append("nutrition meal planning healthy diet")
        elif planning_decision.topic == "Health Habits":
            query_parts.append("healthy habits lifestyle wellness")
        
        # Add theme context
        if planning_decision.theme == "Struggle Support":
            query_parts.append("motivation support tips")
        elif planning_decision.theme == "Progress Celebration":
            query_parts.append("success stories achievements")
        elif planning_decision.theme == "Habit Building":
            query_parts.append("building habits consistency")
        
        # Add user goals
        if user_goals:
            query_parts.extend(user_goals[:2])  # Add first 2 goals
        
        # Add health score context
        if health_analysis.overall_health_score < 50:
            query_parts.append("beginner easy")
        elif health_analysis.overall_health_score > 75:
            query_parts.append("advanced expert")
        
        return " ".join(query_parts)
    
    def _get_tone_description(self, tone: str) -> str:
        """Get description for the selected tone"""
        descriptions = {
            "Sama": "Gentle, peaceful approach inspired by Buddha's middle path",
            "Dana": "Generous, giving approach like a wise teacher",
            "Dhanda": "Firm, disciplinary approach like a strict guru",
            "Bedha": "Strategic, analytical approach like Chanakya's tactics"
        }
        return descriptions.get(tone, descriptions["Sama"])
    
    def _get_tone_characteristics(self, tone: str) -> list:
        """Get characteristics for the selected tone"""
        characteristics = {
            "Sama": ["compassionate", "balanced", "non-judgmental", "patient"],
            "Dana": ["encouraging", "supportive", "educational", "nurturing"],
            "Dhanda": ["direct", "firm", "challenging", "accountable"],
            "Bedha": ["strategic", "analytical", "data-driven", "systematic"]
        }
        return characteristics.get(tone, characteristics["Sama"])
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "AI Planning Agent",
            "type": AgentType.PLANNING,
            "description": "AI-powered planning agent for health guidance decisions",
            "capabilities": [
                "Theme determination",
                "Topic selection",
                "Tone selection (Indian historical context)",
                "Timing optimization",
                "Health data analysis"
            ],
            "supported_tones": ["Sama", "Dana", "Dhanda", "Bedha"],
            "supported_topics": ["Workout Plan", "Meal Plan", "Health Habits"],
            "model": "gpt-5"
        }