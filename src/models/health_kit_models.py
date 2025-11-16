# src/models/health_kit_models.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum

class HealthMetricType(str, Enum):
    STEPS = "steps"
    CALORIES_BURNED = "calories_burned"
    CALORIES_CONSUMED = "calories_consumed"
    HEART_RATE = "heart_rate"
    WEIGHT = "weight"
    BODY_FAT = "body_fat"
    MUSCLE_MASS = "muscle_mass"
    SLEEP_HOURS = "sleep_hours"
    WORKOUT_DURATION = "workout_duration"
    WATER_INTAKE = "water_intake"
    BLOOD_PRESSURE_SYSTOLIC = "blood_pressure_systolic"
    BLOOD_PRESSURE_DIASTOLIC = "blood_pressure_diastolic"

class HealthMetric(BaseModel):
    """Individual health metric from Apple Health Kit"""
    type: HealthMetricType
    value: float
    unit: str
    timestamp: datetime
    source: str = "Apple Health Kit"
    metadata: Optional[Dict[str, Any]] = None

class HealthKitData(BaseModel):
    """Complete health data structure from Apple Health Kit"""
    user_id: str
    date: date
    metrics: List[HealthMetric]
    summary: Optional[str] = None
    
    def get_metric_by_type(self, metric_type: HealthMetricType) -> Optional[HealthMetric]:
        """Get specific metric by type"""
        for metric in self.metrics:
            if metric.type == metric_type:
                return metric
        return None
    
    def get_daily_steps(self) -> Optional[int]:
        """Get daily steps count"""
        steps_metric = self.get_metric_by_type(HealthMetricType.STEPS)
        return int(steps_metric.value) if steps_metric else None
    
    def get_daily_calories_burned(self) -> Optional[float]:
        """Get daily calories burned"""
        calories_metric = self.get_metric_by_type(HealthMetricType.CALORIES_BURNED)
        return calories_metric.value if calories_metric else None
    
    def get_daily_calories_consumed(self) -> Optional[float]:
        """Get daily calories consumed"""
        calories_metric = self.get_metric_by_type(HealthMetricType.CALORIES_CONSUMED)
        return calories_metric.value if calories_metric else None
    
    def get_weight(self) -> Optional[float]:
        """Get current weight"""
        weight_metric = self.get_metric_by_type(HealthMetricType.WEIGHT)
        return weight_metric.value if weight_metric else None
    
    def get_sleep_hours(self) -> Optional[float]:
        """Get sleep hours"""
        sleep_metric = self.get_metric_by_type(HealthMetricType.SLEEP_HOURS)
        return sleep_metric.value if sleep_metric else None

class HealthTrend(BaseModel):
    """Health trend analysis over time"""
    metric_type: HealthMetricType
    current_value: float
    previous_value: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    change_percentage: float
    trend_strength: str  # "strong", "moderate", "weak"

class HealthAnalysis(BaseModel):
    """Comprehensive health analysis"""
    user_id: str
    analysis_date: date
    overall_health_score: float  # 0-100
    trends: List[HealthTrend]
    recommendations: List[str]
    concerns: List[str]
    achievements: List[str]
    next_goals: List[str]

