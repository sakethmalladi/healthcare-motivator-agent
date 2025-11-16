# src/tools/apple_health_kit_mock.py

import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from src.models.health_kit_models import (
    HealthKitData, HealthMetric, HealthMetricType, 
    HealthAnalysis, HealthTrend
)

class AppleHealthKitMock:
    """Mock Apple Health Kit data generator for testing"""
    
    def __init__(self):
        self.base_weight = 70.0  # kg
        self.base_steps = 5000
        self.base_calories_burned = 2000
        self.base_calories_consumed = 2200
        self.base_sleep_hours = 7.5
        self.base_heart_rate = 75
    
    def generate_health_data(self, user_id: str, days_ago: int = 0, 
                           health_scenario: str = "normal") -> HealthKitData:
        """Generate mock health data for a specific day"""
        
        target_date = date.today() - timedelta(days=days_ago)
        
        # Generate data based on scenario
        if health_scenario == "excellent":
            metrics = self._generate_excellent_metrics(target_date)
        elif health_scenario == "struggling":
            metrics = self._generate_struggling_metrics(target_date)
        elif health_scenario == "progress":
            metrics = self._generate_progress_metrics(target_date, days_ago)
        elif health_scenario == "crisis":
            metrics = self._generate_crisis_metrics(target_date)
        else:  # normal
            metrics = self._generate_normal_metrics(target_date)
        
        return HealthKitData(
            user_id=user_id,
            date=target_date,
            metrics=metrics,
            summary=self._generate_summary(metrics, health_scenario)
        )
    
    def _generate_excellent_metrics(self, target_date: date) -> List[HealthMetric]:
        """Generate excellent health metrics"""
        return [
            HealthMetric(
                type=HealthMetricType.STEPS,
                value=random.randint(12000, 15000),
                unit="count",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_BURNED,
                value=random.randint(2500, 3000),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_CONSUMED,
                value=random.randint(2000, 2300),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WEIGHT,
                value=random.uniform(68.0, 72.0),
                unit="kg",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.SLEEP_HOURS,
                value=random.uniform(7.5, 9.0),
                unit="hours",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.HEART_RATE,
                value=random.randint(60, 70),
                unit="bpm",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WORKOUT_DURATION,
                value=random.randint(45, 90),
                unit="minutes",
                timestamp=datetime.combine(target_date, datetime.min.time())
            )
        ]
    
    def _generate_struggling_metrics(self, target_date: date) -> List[HealthMetric]:
        """Generate struggling health metrics"""
        return [
            HealthMetric(
                type=HealthMetricType.STEPS,
                value=random.randint(2000, 4000),
                unit="count",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_BURNED,
                value=random.randint(1200, 1800),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_CONSUMED,
                value=random.randint(2500, 3200),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WEIGHT,
                value=random.uniform(75.0, 85.0),
                unit="kg",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.SLEEP_HOURS,
                value=random.uniform(5.0, 6.5),
                unit="hours",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.HEART_RATE,
                value=random.randint(80, 95),
                unit="bpm",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WORKOUT_DURATION,
                value=0,
                unit="minutes",
                timestamp=datetime.combine(target_date, datetime.min.time())
            )
        ]
    
    def _generate_progress_metrics(self, target_date: date, days_ago: int) -> List[HealthMetric]:
        """Generate progress health metrics (improving over time)"""
        # Progress factor: more recent = better metrics
        progress_factor = max(0.1, 1.0 - (days_ago * 0.1))
        
        return [
            HealthMetric(
                type=HealthMetricType.STEPS,
                value=int(5000 + (5000 * progress_factor) + random.randint(-1000, 1000)),
                unit="count",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_BURNED,
                value=2000 + (500 * progress_factor) + random.randint(-200, 200),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_CONSUMED,
                value=2200 - (200 * progress_factor) + random.randint(-200, 200),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WEIGHT,
                value=75.0 - (2.0 * progress_factor) + random.uniform(-1.0, 1.0),
                unit="kg",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.SLEEP_HOURS,
                value=6.5 + (1.0 * progress_factor) + random.uniform(-0.5, 0.5),
                unit="hours",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.HEART_RATE,
                value=int(80 - (5 * progress_factor) + random.randint(-5, 5)),
                unit="bpm",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WORKOUT_DURATION,
                value=int(20 * progress_factor) + random.randint(0, 30),
                unit="minutes",
                timestamp=datetime.combine(target_date, datetime.min.time())
            )
        ]
    
    def _generate_crisis_metrics(self, target_date: date) -> List[HealthMetric]:
        """Generate crisis health metrics"""
        return [
            HealthMetric(
                type=HealthMetricType.STEPS,
                value=random.randint(500, 2000),
                unit="count",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_BURNED,
                value=random.randint(800, 1200),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_CONSUMED,
                value=random.randint(3000, 4000),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WEIGHT,
                value=random.uniform(85.0, 95.0),
                unit="kg",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.SLEEP_HOURS,
                value=random.uniform(4.0, 6.0),
                unit="hours",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.HEART_RATE,
                value=random.randint(90, 110),
                unit="bpm",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WORKOUT_DURATION,
                value=0,
                unit="minutes",
                timestamp=datetime.combine(target_date, datetime.min.time())
            )
        ]
    
    def _generate_normal_metrics(self, target_date: date) -> List[HealthMetric]:
        """Generate normal health metrics"""
        return [
            HealthMetric(
                type=HealthMetricType.STEPS,
                value=random.randint(6000, 9000),
                unit="count",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_BURNED,
                value=random.randint(1800, 2200),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.CALORIES_CONSUMED,
                value=random.randint(2000, 2500),
                unit="kcal",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WEIGHT,
                value=random.uniform(70.0, 75.0),
                unit="kg",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.SLEEP_HOURS,
                value=random.uniform(6.5, 8.0),
                unit="hours",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.HEART_RATE,
                value=random.randint(70, 85),
                unit="bpm",
                timestamp=datetime.combine(target_date, datetime.min.time())
            ),
            HealthMetric(
                type=HealthMetricType.WORKOUT_DURATION,
                value=random.randint(20, 45),
                unit="minutes",
                timestamp=datetime.combine(target_date, datetime.min.time())
            )
        ]
    
    def _generate_summary(self, metrics: List[HealthMetric], scenario: str) -> str:
        """Generate a summary of the health data"""
        steps = next((m.value for m in metrics if m.type == HealthMetricType.STEPS), 0)
        weight = next((m.value for m in metrics if m.type == HealthMetricType.WEIGHT), 0)
        sleep = next((m.value for m in metrics if m.type == HealthMetricType.SLEEP_HOURS), 0)
        
        summary_parts = [f"Steps: {int(steps)}", f"Weight: {weight:.1f}kg", f"Sleep: {sleep:.1f}h"]
        
        if scenario == "excellent":
            summary_parts.append("Excellent health day!")
        elif scenario == "struggling":
            summary_parts.append("Challenging day, needs support")
        elif scenario == "progress":
            summary_parts.append("Making steady progress")
        elif scenario == "crisis":
            summary_parts.append("Health crisis, immediate attention needed")
        else:
            summary_parts.append("Normal health day")
        
        return " | ".join(summary_parts)
    
    def generate_health_analysis(self, current_data: HealthKitData, 
                                previous_data: HealthKitData = None) -> HealthAnalysis:
        """Generate health analysis from the data"""
        
        # Calculate health score
        health_score = self._calculate_health_score(current_data)
        
        # Analyze trends
        trends = []
        if previous_data:
            trends = self._analyze_trends(current_data, previous_data)
        
        # Generate recommendations, concerns, and achievements
        recommendations = self._generate_recommendations(current_data, health_score)
        concerns = self._identify_concerns(current_data, health_score)
        achievements = self._identify_achievements(current_data, health_score)
        next_goals = self._suggest_next_goals(current_data, health_score)
        
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
    
    def _analyze_trends(self, current: HealthKitData, previous: HealthKitData) -> List[HealthTrend]:
        """Analyze trends between current and previous data"""
        trends = []
        
        # Steps trend
        current_steps = current.get_daily_steps()
        previous_steps = previous.get_daily_steps()
        if current_steps and previous_steps:
            change = ((current_steps - previous_steps) / previous_steps) * 100
            trends.append(HealthTrend(
                metric_type=HealthMetricType.STEPS,
                current_value=current_steps,
                previous_value=previous_steps,
                trend_direction="increasing" if change > 0 else "decreasing",
                change_percentage=change,
                trend_strength="strong" if abs(change) > 20 else "moderate"
            ))
        
        return trends
    
    def _generate_recommendations(self, data: HealthKitData, health_score: float) -> List[str]:
        """Generate health recommendations"""
        recommendations = []
        
        steps = data.get_daily_steps()
        if steps and steps < 5000:
            recommendations.append("Increase daily steps to at least 5000")
        
        sleep = data.get_sleep_hours()
        if sleep and sleep < 7:
            recommendations.append("Aim for 7-9 hours of sleep nightly")
        
        if health_score < 50:
            recommendations.append("Consider consulting a health professional")
        
        return recommendations
    
    def _identify_concerns(self, data: HealthKitData, health_score: float) -> List[str]:
        """Identify health concerns"""
        concerns = []
        
        steps = data.get_daily_steps()
        if steps and steps < 3000:
            concerns.append("Very low daily activity level")
        
        if health_score < 30:
            concerns.append("Critical health score - immediate attention needed")
        
        return concerns
    
    def _identify_achievements(self, data: HealthKitData, health_score: float) -> List[str]:
        """Identify health achievements"""
        achievements = []
        
        steps = data.get_daily_steps()
        if steps and steps >= 10000:
            achievements.append("Met daily step goal of 10,000 steps")
        
        if health_score >= 80:
            achievements.append("Excellent overall health score")
        
        return achievements
    
    def _suggest_next_goals(self, data: HealthKitData, health_score: float) -> List[str]:
        """Suggest next health goals"""
        goals = []
        
        steps = data.get_daily_steps()
        if steps and steps < 10000:
            goals.append("Reach 10,000 daily steps consistently")
        
        if health_score < 70:
            goals.append("Improve overall health score to 70+")
        
        return goals

