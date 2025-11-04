# src/agents/planning_agent.py

from typing import Dict, Any
from src.models.agent_models import PlanningRequest, PlanningResponse, PlanningDecision, AgentType
from src.models.health_kit_models import HealthAnalysis
from src.tools.planning_tool import PlanningTool, IndianTone, HealthTopic, HealthTheme

class PlanningAgent:
    """AI Planning Agent for determining theme, topic, tone, and timing"""
    
    def __init__(self):
        self.planning_tool = PlanningTool()
        self.tone_descriptions = self.planning_tool.tone_descriptions
    
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
            
            # Use PlanningTool's deterministic logic instead of AI parsing
            theme = self.planning_tool.determine_theme(health_analysis)
            # Improve topic selection by considering user goals
            topic = self._select_topic_with_goals(health_analysis, theme, request.user_goals)
            tone = self.planning_tool.select_tone(health_analysis, theme, topic)
            timing = self.planning_tool.determine_timing(health_analysis, theme)
            
            # Build reasoning based on health analysis
            reasoning = self._build_reasoning(health_analysis, theme, topic, tone, request)
            
            # Calculate confidence based on health score and data quality
            confidence_score = self._calculate_confidence(health_analysis, request)
            
            # Create the planning decision
            planning_decision = PlanningDecision(
                theme=theme.value,
                topic=topic.value,
                tone=tone.value,
                tone_description=self.tone_descriptions[tone]["description"],
                tone_characteristics=self.tone_descriptions[tone]["characteristics"],
                timing=timing,
                reasoning=reasoning,
                confidence_score=confidence_score
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
    
    def _build_reasoning(self, health_analysis, theme, topic, tone, request: PlanningRequest) -> str:
        """Build reasoning for the planning decision"""
        reasoning_parts = []
        
        reasoning_parts.append(f"Health score: {health_analysis.overall_health_score:.1f}/100")
        
        if health_analysis.achievements:
            reasoning_parts.append(f"Achievements: {', '.join(health_analysis.achievements[:2])}")
        
        if health_analysis.concerns:
            reasoning_parts.append(f"Concerns: {', '.join(health_analysis.concerns[:2])}")
        
        reasoning_parts.append(f"Selected {theme.value} theme because health score indicates {self._get_theme_rationale(theme)}")
        reasoning_parts.append(f"Selected {topic.value} topic based on health data analysis")
        reasoning_parts.append(f"Selected {tone.value} tone ({self.tone_descriptions[tone]['description']})")
        
        if request.user_goals:
            reasoning_parts.append(f"User goals: {', '.join(request.user_goals[:2])}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_theme_rationale(self, theme) -> str:
        """Get rationale for theme selection"""
        rationale_map = {
            HealthTheme.CRISIS_INTERVENTION: "critical intervention needed",
            HealthTheme.STRUGGLE_SUPPORT: "user is struggling and needs support",
            HealthTheme.MOTIVATION_NEEDED: "moderate progress requiring motivation",
            HealthTheme.HABIT_BUILDING: "good progress, focus on habit building",
            HealthTheme.PROGRESS_CELEBRATION: "excellent progress deserving celebration"
        }
        return rationale_map.get(theme, "appropriate intervention level")
    
    def _select_topic_with_goals(self, health_analysis, theme, user_goals) -> HealthTopic:
        """Select topic considering user goals"""
        # First try PlanningTool's logic
        topic = self.planning_tool.select_topic(health_analysis, theme)
        
        # Override based on user goals if they're clear
        if user_goals:
            goals_text = " ".join(user_goals).lower()
            
            # Check for workout-related keywords
            if any(word in goals_text for word in ["workout", "exercise", "fitness", "run", "strength", "muscle", "gym", "training"]):
                return HealthTopic.WORKOUT_PLAN
            
            # Check for meal/nutrition-related keywords
            if any(word in goals_text for word in ["meal", "diet", "nutrition", "eat", "food", "calorie", "weight loss"]):
                return HealthTopic.MEAL_PLAN
            
            # Check for habit-related keywords
            if any(word in goals_text for word in ["habit", "routine", "lifestyle", "daily", "consistency"]):
                return HealthTopic.HEALTH_HABITS
        
        return topic
    
    def _calculate_confidence(self, health_analysis, request: PlanningRequest) -> float:
        """Calculate confidence score based on data quality and health score"""
        confidence = 0.7  # Base confidence
        
        # Increase confidence if health score is clear
        if health_analysis.overall_health_score < 30 or health_analysis.overall_health_score > 85:
            confidence += 0.15  # Clear cases
        
        # Increase confidence if we have good data
        if health_analysis.recommendations and len(health_analysis.recommendations) > 0:
            confidence += 0.05
        
        # Increase confidence if user goals are clear
        if request.user_goals and len(request.user_goals) > 0:
            confidence += 0.05
        
        # Decrease confidence if concerns are high
        if len(health_analysis.concerns) > 3:
            confidence -= 0.05
        
        return min(0.95, max(0.5, confidence))
    
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
            "model": "gpt-4o-mini"
        }
