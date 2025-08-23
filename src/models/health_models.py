from pydantic import BaseModel
from typing import List, Dict

class HealthData(BaseModel):
    steps: int
    calories: int
    workouts: int
    weight: float = None
    goal_steps: int = None
    goal_weight: float = None

class MotivationRequest(BaseModel):
    user_id: str
    previous_data: str
    current_data: str
    action_taken: str
    next_action: str
    custom_instruction: str
    goal: str
    progress: str

class MotivationResponse(BaseModel):
    prompt: str
    web_results: List[Dict[str, str]]
    youtube_videos: List[Dict[str, str]]
