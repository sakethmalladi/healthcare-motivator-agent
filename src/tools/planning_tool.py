# src/tools/planning_tool.py

import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, time, date
from enum import Enum
from agents import Agent, Runner
from src.models.health_kit_models import HealthKitData, HealthAnalysis, HealthTrend, HealthMetricType

class IndianTone(str, Enum):
    """Indian historical context tones for health guidance"""
    SAMA = "Sama"      # Gentle, peaceful approach (Buddha's middle path)
    DANA = "Dana"      # Generous, giving approach (wise teacher)
    DHANDA = "Dhanda"  # Firm, disciplinary approach (strict guru)
    BEDHA = "Bedha"    # Strategic, analytical approach (Chanakya's tactics)

class HealthTopic(str, Enum):
    """Health planning topics"""
    WORKOUT_PLAN = "Workout Plan"
    MEAL_PLAN = "Meal Plan"
    HEALTH_HABITS = "Health Habits"

class HealthTheme(str, Enum):
    """Health situation themes"""
    MOTIVATION_NEEDED = "Motivation Needed"
    PROGRESS_CELEBRATION = "Progress Celebration"
    STRUGGLE_SUPPORT = "Struggle Support"
    GOAL_ADJUSTMENT = "Goal Adjustment"
    HABIT_BUILDING = "Habit Building"
    CRISIS_INTERVENTION = "Crisis Intervention"

class PlanningTool:
    """Core planning tool that determines theme, topic, tone, and timing"""
    
    def __init__(self):
        self.tone_descriptions = {
            IndianTone.SAMA: {
                "description": "Gentle, peaceful approach inspired by Buddha's middle path",
                "characteristics": ["compassionate", "balanced", "non-judgmental", "patient"],
                "use_cases": ["beginner users", "struggling users", "sensitive situations"]
            },
            IndianTone.DANA: {
                "description": "Generous, giving approach like a wise teacher",
                "characteristics": ["encouraging", "supportive", "educational", "nurturing"],
                "use_cases": ["progress celebration", "learning moments", "habit building"]
            },
            IndianTone.DHANDA: {
                "description": "Firm, disciplinary approach like a strict guru",
                "characteristics": ["direct", "firm", "challenging", "accountable"],
                "use_cases": ["lack of progress", "excuse-making", "need for discipline"]
            },
            IndianTone.BEDHA: {
                "description": "Strategic, analytical approach like Chanakya's tactics",
                "characteristics": ["strategic", "analytical", "data-driven", "systematic"],
                "use_cases": ["complex goals", "plateau situations", "optimization needs"]
            }
        }
        
        # Initialize LLM agent for health analysis (skip in active event loop environments)
        try:
            loop = asyncio.get_running_loop()
            if loop and loop.is_running():
                self.health_analysis_agent = None
                self.runner = None
            else:
                self.health_analysis_agent = Agent(
                    name="HealthAnalysisAgent",
                    instructions=self._get_health_analysis_instructions(),
                    tools=[],
                    model="gpt-4o-mini"
                )
                self.runner = Runner()
        except RuntimeError:
            # No running loop; safe to initialize
            self.health_analysis_agent = Agent(
                name="HealthAnalysisAgent",
                instructions=self._get_health_analysis_instructions(),
                tools=[],
                model="gpt-4o-mini"
            )
            self.runner = Runner()
    
    def _get_health_analysis_instructions(self) -> str:
        """Get agent instructions for health analysis"""
        return """
        You are a specialized Health Analysis Agent for comprehensive health data evaluation.
        
        Your role is to:
        1. Analyze all health metrics comprehensively (steps, weight, sleep, calories, etc.)
        2. Calculate an overall health score (0-100) based on comprehensive analysis of all metrics
        3. Identify trends by comparing current vs previous data
        4. Generate specific, actionable recommendations
        5. Identify key concerns that need attention
        6. Recognize achievements and progress made
        7. Suggest realistic next goals
        
        IMPORTANT:
        - Analyze ALL available metrics comprehensively
        - Consider the relationship between different metrics
        - Provide detailed, specific recommendations
        - Be realistic and actionable in your suggestions
        - Consider both positive and negative trends
        - Return your response in the exact JSON format specified in the prompt
        """
    
    def analyze_health_data(self, current_data: HealthKitData, previous_data: Optional[HealthKitData] = None) -> HealthAnalysis:
        """Analyze health data using LLM to determine overall health score and trends"""
        
        try:
            # If runner is unavailable (e.g., test async loop), use rule-based immediately
            if not self.runner or not self.health_analysis_agent:
                return self._analyze_health_data_rule_based(current_data, previous_data)
            
            # Build prompt for health analysis
            prompt = self._build_health_analysis_prompt(current_data, previous_data)
            
            # Call LLM for health analysis
            response = self.runner.run_sync(self.health_analysis_agent, prompt)
            
            # Parse LLM response
            parsed_response = self._parse_health_analysis_response(response.final_output)
            
            # Create HealthAnalysis object from LLM response
            return self._create_health_analysis_from_llm(
                current_data=current_data,
                previous_data=previous_data,
                health_analysis_data=parsed_response
            )
        except Exception as e:
            # Fallback to rule-based analysis if LLM fails
            print(f"Warning: LLM health analysis failed: {e}. Falling back to rule-based analysis.")
            return self._analyze_health_data_rule_based(current_data, previous_data)
    
    def _analyze_health_data_rule_based(self, current_data: HealthKitData, previous_data: Optional[HealthKitData] = None) -> HealthAnalysis:
        """Fallback rule-based health analysis"""
        # Calculate health score based on various metrics
        health_score = self._calculate_health_score(current_data)
        
        # Analyze trends if previous data is available
        trends = []
        if previous_data:
            trends = self._analyze_trends(current_data, previous_data)
        
        # Generate recommendations, concerns, and achievements
        recommendations = self._generate_recommendations(current_data, trends)
        concerns = self._identify_concerns(current_data, trends)
        achievements = self._identify_achievements(current_data, trends)
        next_goals = self._suggest_next_goals(current_data, trends)
        
        return HealthAnalysis(
            user_id=current_data.user_id,
            analysis_date=current_data.date,
            overall_health_score=health_score,
            trends=trends,
            recommendations=recommendations,
            concerns=concerns,
            achievements=achievements,
            next_goals=next_goals
        )
    
    def determine_theme(self, analysis: HealthAnalysis) -> HealthTheme:
        """Determine the theme based on health analysis"""
        
        if analysis.overall_health_score < 30:
            return HealthTheme.CRISIS_INTERVENTION
        elif analysis.overall_health_score < 50:
            return HealthTheme.STRUGGLE_SUPPORT
        elif analysis.overall_health_score < 70:
            return HealthTheme.MOTIVATION_NEEDED
        elif analysis.overall_health_score < 85:
            return HealthTheme.HABIT_BUILDING
        else:
            return HealthTheme.PROGRESS_CELEBRATION
    
    def select_topic(self, analysis: HealthAnalysis, theme: HealthTheme) -> HealthTopic:
        """Select the most appropriate topic based on analysis and theme"""
        
        # Analyze which area needs most attention
        workout_score = self._calculate_workout_score(analysis)
        nutrition_score = self._calculate_nutrition_score(analysis)
        habits_score = self._calculate_habits_score(analysis)
        
        if theme == HealthTheme.CRISIS_INTERVENTION:
            # Focus on habits first in crisis
            return HealthTopic.HEALTH_HABITS
        elif workout_score < nutrition_score and workout_score < habits_score:
            return HealthTopic.WORKOUT_PLAN
        elif nutrition_score < habits_score:
            return HealthTopic.MEAL_PLAN
        else:
            return HealthTopic.HEALTH_HABITS
    
    def select_tone(self, analysis: HealthAnalysis, theme: HealthTheme, topic: HealthTopic) -> IndianTone:
        """Select appropriate Indian tone based on context"""
        
        if theme == HealthTheme.CRISIS_INTERVENTION:
            return IndianTone.SAMA  # Gentle approach for crisis
        elif theme == HealthTheme.STRUGGLE_SUPPORT:
            return IndianTone.DANA  # Supportive approach for struggles
        elif theme == HealthTheme.PROGRESS_CELEBRATION:
            return IndianTone.DANA  # Encouraging for progress
        elif analysis.overall_health_score < 40:
            return IndianTone.DHANDA  # Firm approach for low scores
        elif len(analysis.concerns) > 3:
            return IndianTone.BEDHA  # Strategic approach for complex issues
        else:
            return IndianTone.SAMA  # Default to gentle approach
    
    def determine_timing(self, analysis: HealthAnalysis, theme: HealthTheme) -> Dict[str, any]:
        """Determine when to send notifications based on context"""
        
        base_times = {
            "morning": time(8, 0),      # 8:00 AM
            "afternoon": time(14, 0),   # 2:00 PM
            "evening": time(18, 0),     # 6:00 PM
            "night": time(21, 0)        # 9:00 PM
        }
        
        if theme == HealthTheme.CRISIS_INTERVENTION:
            return {
                "immediate": True,
                "scheduled_times": [base_times["morning"], base_times["evening"]],
                "frequency": "twice_daily"
            }
        elif theme == HealthTheme.STRUGGLE_SUPPORT:
            return {
                "immediate": False,
                "scheduled_times": [base_times["morning"]],
                "frequency": "daily"
            }
        elif theme == HealthTheme.PROGRESS_CELEBRATION:
            return {
                "immediate": True,
                "scheduled_times": [base_times["evening"]],
                "frequency": "daily"
            }
        else:
            return {
                "immediate": False,
                "scheduled_times": [base_times["morning"]],
                "frequency": "daily"
            }
    
    def create_planning_context(self, analysis: HealthAnalysis, theme: HealthTheme, 
                              topic: HealthTopic, tone: IndianTone, timing: Dict[str, any]) -> Dict[str, any]:
        """Create comprehensive planning context for agents"""
        
        return {
            "theme": theme.value,
            "topic": topic.value,
            "tone": tone.value,
            "tone_description": self.tone_descriptions[tone]["description"],
            "tone_characteristics": self.tone_descriptions[tone]["characteristics"],
            "timing": timing,
            "health_score": analysis.overall_health_score,
            "trends": [trend.dict() for trend in analysis.trends],
            "recommendations": analysis.recommendations,
            "concerns": analysis.concerns,
            "achievements": analysis.achievements,
            "next_goals": analysis.next_goals
        }
    
    def _calculate_health_score(self, data: HealthKitData) -> float:
        """Calculate overall health score (0-100)"""
        score = 50  # Base score
        
        # Steps scoring
        steps = data.get_daily_steps()
        if steps:
            if steps >= 10000:
                score += 20
            elif steps >= 7500:
                score += 15
            elif steps >= 5000:
                score += 10
            else:
                score -= 10
        
        # Weight scoring (assuming 70kg is healthy)
        weight = data.get_weight()
        if weight:
            if 60 <= weight <= 80:
                score += 15
            elif 55 <= weight <= 85:
                score += 10
            else:
                score -= 15
        
        # Sleep scoring
        sleep = data.get_sleep_hours()
        if sleep:
            if 7 <= sleep <= 9:
                score += 15
            elif 6 <= sleep <= 10:
                score += 10
            else:
                score -= 10
        
        return max(0, min(100, score))
    
    def _analyze_trends(self, current: HealthKitData, previous: HealthKitData) -> List:
        """Analyze trends between current and previous data"""
        # Implementation for trend analysis
        return []
    
    def _generate_recommendations(self, data: HealthKitData, trends: List) -> List[str]:
        """Generate health recommendations"""
        recommendations = []
        
        steps = data.get_daily_steps()
        if steps and steps < 5000:
            recommendations.append("Increase daily steps to at least 5000")
        
        sleep = data.get_sleep_hours()
        if sleep and sleep < 7:
            recommendations.append("Aim for 7-9 hours of sleep nightly")
        
        return recommendations
    
    def _identify_concerns(self, data: HealthKitData, trends: List) -> List[str]:
        """Identify health concerns"""
        concerns = []
        
        steps = data.get_daily_steps()
        if steps and steps < 3000:
            concerns.append("Very low daily activity level")
        
        return concerns
    
    def _identify_achievements(self, data: HealthKitData, trends: List) -> List[str]:
        """Identify health achievements"""
        achievements = []
        
        steps = data.get_daily_steps()
        if steps and steps >= 10000:
            achievements.append("Met daily step goal of 10,000 steps")
        
        return achievements
    
    def _suggest_next_goals(self, data: HealthKitData, trends: List) -> List[str]:
        """Suggest next health goals"""
        goals = []
        
        steps = data.get_daily_steps()
        if steps and steps < 10000:
            goals.append("Reach 10,000 daily steps consistently")
        
        return goals
    
    def _calculate_workout_score(self, analysis: HealthAnalysis) -> float:
        """Calculate workout-related health score"""
        # Implementation for workout scoring
        return 50.0
    
    def _calculate_nutrition_score(self, analysis: HealthAnalysis) -> float:
        """Calculate nutrition-related health score"""
        # Implementation for nutrition scoring
        return 50.0
    
    def _calculate_habits_score(self, analysis: HealthAnalysis) -> float:
        """Calculate habits-related health score"""
        # Implementation for habits scoring
        return 50.0
    
    def _build_health_analysis_prompt(self, current_data: HealthKitData, previous_data: Optional[HealthKitData] = None) -> str:
        """Build prompt for health analysis LLM"""
        
        # Build health data section
        current_steps = current_data.get_daily_steps()
        current_weight = current_data.get_weight()
        current_sleep = current_data.get_sleep_hours()
        current_calories_burned = current_data.get_daily_calories_burned()
        current_calories_consumed = current_data.get_daily_calories_consumed()
        
        health_data_section = f"""
CURRENT HEALTH DATA:
- Steps: {current_steps if current_steps else 'N/A'}
- Weight: {current_weight if current_weight else 'N/A'} kg
- Sleep: {current_sleep if current_sleep else 'N/A'} hours
- Calories Burned: {current_calories_burned if current_calories_burned else 'N/A'}
- Calories Consumed: {current_calories_consumed if current_calories_consumed else 'N/A'}
- Date: {current_data.date}
"""
        
        if previous_data:
            prev_steps = previous_data.get_daily_steps()
            prev_weight = previous_data.get_weight()
            prev_sleep = previous_data.get_sleep_hours()
            health_data_section += f"""
PREVIOUS HEALTH DATA:
- Steps: {prev_steps if prev_steps else 'N/A'}
- Weight: {prev_weight if prev_weight else 'N/A'} kg
- Sleep: {prev_sleep if prev_sleep else 'N/A'} hours
- Date: {previous_data.date}
"""
        
        return f"""
{health_data_section}

Please analyze this health data comprehensively and provide your analysis in the following JSON format:

{{
    "overall_health_score": <float 0-100>,
    "trends": [
        {{
            "metric_type": "<steps|weight|sleep|calories_burned|calories_consumed>",
            "current_value": <float>,
            "previous_value": <float or null>,
            "trend_direction": "<increasing|decreasing|stable>",
            "change_percentage": <float>,
            "trend_strength": "<strong|moderate|weak>"
        }}
    ],
    "recommendations": ["<recommendation 1>", "<recommendation 2>", ...],
    "concerns": ["<concern 1>", "<concern 2>", ...],
    "achievements": ["<achievement 1>", "<achievement 2>", ...],
    "next_goals": ["<goal 1>", "<goal 2>", ...]
}}

IMPORTANT INSTRUCTIONS:
- Analyze ALL metrics comprehensively to determine overall health score (0-100)
- Consider the relationship between different metrics
- Identify trends by comparing current and previous data (if available)
- Generate specific, actionable recommendations
- Identify key concerns that need attention
- Recognize achievements and progress made
- Suggest realistic next goals

Return ONLY valid JSON without any additional text or markdown formatting.
"""
    
    def _parse_health_analysis_response(self, agent_output: str) -> Dict[str, Any]:
        """Parse the LLM response for health analysis"""
        default_response = {
            "overall_health_score": 50.0,
            "trends": [],
            "recommendations": [],
            "concerns": [],
            "achievements": [],
            "next_goals": []
        }
        
        try:
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
            
            # Find JSON object boundaries
            if "{" in agent_output and "}" in agent_output:
                start = agent_output.find("{")
                end = agent_output.rfind("}") + 1
                agent_output = agent_output[start:end]
            
            # Parse JSON
            parsed = json.loads(agent_output)
            
            if not isinstance(parsed, dict):
                return default_response
            
            return parsed
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Warning: Failed to parse health analysis response as JSON: {str(e)}")
            return default_response
    
    def _create_health_analysis_from_llm(
        self,
        current_data: HealthKitData,
        previous_data: Optional[HealthKitData],
        health_analysis_data: Dict[str, Any]
    ) -> HealthAnalysis:
        """Create HealthAnalysis object from LLM response"""
        
        # Extract and convert trends
        trends = []
        for trend_data in health_analysis_data.get("trends", []):
            try:
                metric_type_str = trend_data.get("metric_type", "").lower()
                metric_type_map = {
                    "steps": HealthMetricType.STEPS,
                    "weight": HealthMetricType.WEIGHT,
                    "sleep": HealthMetricType.SLEEP_HOURS,
                    "sleep_hours": HealthMetricType.SLEEP_HOURS,
                    "calories_burned": HealthMetricType.CALORIES_BURNED,
                    "calories_consumed": HealthMetricType.CALORIES_CONSUMED,
                    "heart_rate": HealthMetricType.HEART_RATE,
                    "body_fat": HealthMetricType.BODY_FAT,
                    "muscle_mass": HealthMetricType.MUSCLE_MASS,
                    "workout_duration": HealthMetricType.WORKOUT_DURATION,
                    "water_intake": HealthMetricType.WATER_INTAKE
                }
                metric_type = metric_type_map.get(metric_type_str, HealthMetricType.STEPS)
                
                trend = HealthTrend(
                    metric_type=metric_type,
                    current_value=float(trend_data.get("current_value", 0)),
                    previous_value=float(trend_data.get("previous_value", 0)) if trend_data.get("previous_value") is not None else 0,
                    trend_direction=trend_data.get("trend_direction", "stable"),
                    change_percentage=float(trend_data.get("change_percentage", 0)),
                    trend_strength=trend_data.get("trend_strength", "moderate")
                )
                trends.append(trend)
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid trend data: {e}")
                continue
        
        # Extract lists and validate
        recommendations = health_analysis_data.get("recommendations", [])
        concerns = health_analysis_data.get("concerns", [])
        achievements = health_analysis_data.get("achievements", [])
        next_goals = health_analysis_data.get("next_goals", [])
        
        if not isinstance(recommendations, list):
            recommendations = []
        if not isinstance(concerns, list):
            concerns = []
        if not isinstance(achievements, list):
            achievements = []
        if not isinstance(next_goals, list):
            next_goals = []
        
        # Extract and validate health score
        overall_health_score = float(health_analysis_data.get("overall_health_score", 50.0))
        overall_health_score = max(0.0, min(100.0, overall_health_score))
        
        return HealthAnalysis(
            user_id=current_data.user_id,
            analysis_date=current_data.date,
            overall_health_score=overall_health_score,
            trends=trends,
            recommendations=recommendations,
            concerns=concerns,
            achievements=achievements,
            next_goals=next_goals
        )

