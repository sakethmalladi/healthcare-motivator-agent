# src/tools/planning_tool.py

from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
from enum import Enum
from src.models.health_kit_models import HealthKitData, HealthAnalysis

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
    
    def analyze_health_data(self, current_data: HealthKitData, previous_data: Optional[HealthKitData] = None) -> HealthAnalysis:
        """Analyze health data and determine overall health score and trends"""
        
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

