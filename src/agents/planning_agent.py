# src/agents/planning_agent.py

import os
from typing import Dict, Any
from agents import Agent, Runner
from src.models.agent_models import PlanningRequest, PlanningResponse, PlanningDecision, AgentType
from src.models.health_kit_models import HealthAnalysis
from src.tools.planning_tool import PlanningTool, IndianTone, HealthTopic, HealthTheme
from src.utils.prompt_builder import build_planning_prompt

class PlanningAgent:
    """AI Planning Agent for determining theme, topic, tone, and timing"""
    
    def __init__(self):
        self.agent = Agent(
            name="PlanningAgent",
            instructions=self._get_agent_instructions(),
            tools=[],  # No external tools needed for planning
            model="gpt-5"  # Using GPT-5 as requested
        )
        self.runner = Runner()
        self.planning_tool = PlanningTool()
    
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
            # First, analyze the health data using the planning tool
            health_analysis = self.planning_tool.analyze_health_data(
                request.health_analysis.get("current_data"),
                request.health_analysis.get("previous_data")
            )
            
            # Use the enhanced prompt builder
            agent_message = build_planning_prompt(
                health_data=request.health_data,
                user_goals=request.user_goals,
                user_preferences=request.user_preferences
            )
            
            # Run the agent
            response = self.runner.run_sync(self.agent, agent_message)
            
            # Parse the agent's response to extract decisions
            decisions = self._parse_agent_response(response.final_output)
            
            # Create the planning decision
            planning_decision = PlanningDecision(
                theme=decisions.get("theme", "Motivation Needed"),
                topic=decisions.get("topic", "Health Habits"),
                tone=decisions.get("tone", "Sama"),
                tone_description=self._get_tone_description(decisions.get("tone", "Sama")),
                tone_characteristics=self._get_tone_characteristics(decisions.get("tone", "Sama")),
                timing=decisions.get("timing", {"immediate": False, "frequency": "daily"}),
                reasoning=decisions.get("reasoning", "Default reasoning"),
                confidence_score=decisions.get("confidence", 0.7)
            )
            
            # Create context for other agents
            context_for_agents = {
                "theme": planning_decision.theme,
                "topic": planning_decision.topic,
                "tone": planning_decision.tone,
                "tone_description": planning_decision.tone_description,
                "tone_characteristics": planning_decision.tone_characteristics,
                "timing": planning_decision.timing,
                "health_score": health_analysis.overall_health_score,
                "recommendations": health_analysis.recommendations,
                "concerns": health_analysis.concerns,
                "achievements": health_analysis.achievements,
                "next_goals": health_analysis.next_goals
            }
            
            return PlanningResponse(
                agent_type=AgentType.PLANNING,
                success=True,
                content=f"Created health plan with {planning_decision.tone} tone for {planning_decision.topic}",
                decision=planning_decision,
                context_for_other_agents=context_for_agents,
                metadata={
                    "health_score": health_analysis.overall_health_score,
                    "confidence": planning_decision.confidence_score,
                    "reasoning": planning_decision.reasoning
                }
            )
            
        except Exception as e:
            return PlanningResponse(
                agent_type=AgentType.PLANNING,
                success=False,
                content=f"Error creating health plan: {str(e)}",
                decision=PlanningDecision(
                    theme="Motivation Needed",
                    topic="Health Habits",
                    tone="Sama",
                    tone_description="Gentle, peaceful approach",
                    tone_characteristics=["compassionate", "balanced"],
                    timing={"immediate": False, "frequency": "daily"},
                    reasoning=f"Error fallback: {str(e)}",
                    confidence_score=0.1
                ),
                context_for_other_agents={},
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
        """Parse the agent's response to extract planning decisions"""
        # Simple parsing - in a more sophisticated implementation, this would use structured output
        decisions = {
            "theme": "Motivation Needed",
            "topic": "Health Habits", 
            "tone": "Sama",
            "timing": {"immediate": False, "frequency": "daily"},
            "reasoning": "Default reasoning from AI agent",
            "confidence": 0.7
        }
        
        # Try to extract decisions from the agent output
        output_lower = agent_output.lower()
        
        # Extract theme
        if "crisis" in output_lower:
            decisions["theme"] = "Crisis Intervention"
        elif "struggle" in output_lower:
            decisions["theme"] = "Struggle Support"
        elif "progress" in output_lower or "celebration" in output_lower:
            decisions["theme"] = "Progress Celebration"
        elif "habit" in output_lower:
            decisions["theme"] = "Habit Building"
        elif "goal" in output_lower:
            decisions["theme"] = "Goal Adjustment"
        
        # Extract topic
        if "workout" in output_lower or "exercise" in output_lower:
            decisions["topic"] = "Workout Plan"
        elif "meal" in output_lower or "nutrition" in output_lower or "diet" in output_lower:
            decisions["topic"] = "Meal Plan"
        elif "habit" in output_lower or "lifestyle" in output_lower:
            decisions["topic"] = "Health Habits"
        
        # Extract tone
        if "sama" in output_lower or "gentle" in output_lower:
            decisions["tone"] = "Sama"
        elif "dana" in output_lower or "generous" in output_lower or "supportive" in output_lower:
            decisions["tone"] = "Dana"
        elif "dhanda" in output_lower or "firm" in output_lower or "strict" in output_lower:
            decisions["tone"] = "Dhanda"
        elif "bedha" in output_lower or "strategic" in output_lower or "analytical" in output_lower:
            decisions["tone"] = "Bedha"
        
        # Extract timing
        if "immediate" in output_lower or "urgent" in output_lower:
            decisions["timing"] = {"immediate": True, "frequency": "twice_daily"}
        elif "daily" in output_lower:
            decisions["timing"] = {"immediate": False, "frequency": "daily"}
        
        # Extract confidence
        if "confidence" in output_lower:
            # Simple confidence extraction
            if "high" in output_lower:
                decisions["confidence"] = 0.9
            elif "medium" in output_lower:
                decisions["confidence"] = 0.7
            elif "low" in output_lower:
                decisions["confidence"] = 0.4
        
        return decisions
    
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
