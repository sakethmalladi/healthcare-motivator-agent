# src/evals/eval_datasets.py

from typing import List, Dict, Any
from dataclasses import dataclass
from src.models.health_kit_models import HealthKitData
from src.tools.apple_health_kit_mock import AppleHealthKitMock

@dataclass
class EvalCase:
    """Single evaluation test case"""
    case_id: str
    name: str
    user_id: str
    health_data: Dict[str, Any]
    custom_instruction: str
    expected_themes: List[str]  # Expected themes that could be selected
    expected_topics: List[str]    # Expected topics that could be selected
    expected_tones: List[str]     # Expected tones that could be selected
    expected_min_agents_successful: int  # Minimum number of agents that should succeed
    description: str = ""

class HealthEvalDataset:
    """Dataset for evaluating health coordinator and agents"""
    
    def __init__(self):
        self.health_kit_mock = AppleHealthKitMock()
        self.eval_cases: List[EvalCase] = []
        self._build_default_dataset()
    
    def _build_default_dataset(self):
        """Build default evaluation dataset"""
        
        # Case 1: Weight Loss Progress
        current_data = self.health_kit_mock.generate_health_data("eval_user_1", 0, "progress")
        previous_data = self.health_kit_mock.generate_health_data("eval_user_1", 1, "struggling")
        
        self.eval_cases.append(EvalCase(
            case_id="weight_loss_progress",
            name="Weight Loss Progress Scenario",
            user_id="eval_user_1",
            health_data={
                "user_id": "eval_user_1",
                "current_data": current_data,
                "previous_data": previous_data,
                "goals": ["Lose 10kg in 6 months", "Build healthy habits"],
                "preferences": {"focus": "sustainable habits"},
                "mood": "motivated",
                "energy_level": 7,
                "challenges": ["portion control"],
                "achievements": ["Lost 0.5kg this week"]
            },
            custom_instruction="Focus on sustainable weight loss",
            expected_themes=["Progress Celebration", "Habit Building"],
            expected_topics=["Meal Plan", "Health Habits"],
            expected_tones=["Sama", "Dana"],
            expected_min_agents_successful=2,
            description="User making progress with weight loss goals"
        ))
        
        # Case 2: Crisis Intervention
        current_data = self.health_kit_mock.generate_health_data("eval_user_2", 0, "crisis")
        previous_data = self.health_kit_mock.generate_health_data("eval_user_2", 1, "excellent")
        
        self.eval_cases.append(EvalCase(
            case_id="crisis_intervention",
            name="Health Crisis Scenario",
            user_id="eval_user_2",
            health_data={
                "user_id": "eval_user_2",
                "current_data": current_data,
                "previous_data": previous_data,
                "goals": ["Get back on track", "Emergency health intervention"],
                "preferences": {"focus": "urgent intervention"},
                "mood": "discouraged",
                "energy_level": 2,
                "challenges": ["motivation", "consistency", "depression"],
                "achievements": ["Was doing great for 3 weeks"]
            },
            custom_instruction="Need urgent motivation to not give up",
            expected_themes=["Crisis Intervention", "Struggle Support"],
            expected_topics=["Health Habits"],
            expected_tones=["Sama"],  # Should be gentle for crisis
            expected_min_agents_successful=2,
            description="User in crisis needing immediate support"
        ))
        
        # Case 3: Fitness Enthusiast
        current_data = self.health_kit_mock.generate_health_data("eval_user_3", 0, "excellent")
        previous_data = self.health_kit_mock.generate_health_data("eval_user_3", 1, "normal")
        
        self.eval_cases.append(EvalCase(
            case_id="fitness_enthusiast",
            name="Fitness Enthusiast Scenario",
            user_id="eval_user_3",
            health_data={
                "user_id": "eval_user_3",
                "current_data": current_data,
                "previous_data": previous_data,
                "goals": ["Run a 10K race in under 50 minutes", "Build endurance"],
                "preferences": {"focus": "endurance and strength"},
                "mood": "energetic",
                "energy_level": 9,
                "challenges": ["time management"],
                "achievements": ["Consistent training for 3 weeks"]
            },
            custom_instruction="Help with advanced training techniques",
            expected_themes=["Progress Celebration", "Habit Building"],
            expected_topics=["Workout Plan"],
            expected_tones=["Dana", "Bedha"],  # Could be supportive or strategic
            expected_min_agents_successful=2,
            description="High-performing user seeking advanced guidance"
        ))
        
        # Case 4: Struggling Beginner
        current_data = self.health_kit_mock.generate_health_data("eval_user_4", 0, "struggling")
        previous_data = self.health_kit_mock.generate_health_data("eval_user_4", 1, "normal")
        
        self.eval_cases.append(EvalCase(
            case_id="struggling_beginner",
            name="Struggling Beginner Scenario",
            user_id="eval_user_4",
            health_data={
                "user_id": "eval_user_4",
                "current_data": current_data,
                "previous_data": previous_data,
                "goals": ["Start exercising regularly", "Eat healthier"],
                "preferences": {"focus": "simple steps"},
                "mood": "frustrated",
                "energy_level": 4,
                "challenges": ["motivation", "consistency", "overwhelm"],
                "achievements": [],
            },
            custom_instruction="Need gentle encouragement and simple steps",
            expected_themes=["Struggle Support", "Motivation Needed"],
            expected_topics=["Health Habits"],
            expected_tones=["Sama"],  # Should be gentle
            expected_min_agents_successful=2,
            description="Beginner struggling with basic habits"
        ))
        
        # Case 5: Muscle Building
        current_data = self.health_kit_mock.generate_health_data("eval_user_5", 0, "excellent")
        previous_data = self.health_kit_mock.generate_health_data("eval_user_5", 1, "normal")
        
        self.eval_cases.append(EvalCase(
            case_id="muscle_building",
            name="Muscle Building Scenario",
            user_id="eval_user_5",
            health_data={
                "user_id": "eval_user_5",
                "current_data": current_data,
                "previous_data": previous_data,
                "goals": ["Build muscle mass and strength", "Progressive overload"],
                "preferences": {"focus": "progressive overload"},
                "mood": "determined",
                "energy_level": 8,
                "challenges": ["form maintenance"],
                "achievements": ["Strength gains visible"]
            },
            custom_instruction="Emphasize progressive overload and recovery",
            expected_themes=["Progress Celebration", "Habit Building"],
            expected_topics=["Workout Plan"],
            expected_tones=["Dana", "Bedha"],  # Could be supportive or strategic
            expected_min_agents_successful=2,
            description="User focused on strength and muscle building"
        ))
    
    def get_all_cases(self) -> List[EvalCase]:
        """Get all evaluation cases"""
        return self.eval_cases
    
    def get_case_by_id(self, case_id: str) -> EvalCase:
        """Get a specific evaluation case by ID"""
        for case in self.eval_cases:
            if case.case_id == case_id:
                return case
        raise ValueError(f"Case {case_id} not found")
    
    def add_case(self, case: EvalCase):
        """Add a custom evaluation case"""
        self.eval_cases.append(case)

