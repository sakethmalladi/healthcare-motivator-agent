# src/models/health_models.py
from pydantic import BaseModel
from typing import List, Dict, Union, Any

class MotivationRequest(BaseModel):
    user_id: str
    previous_data: Union[str, Dict[str, Any]]
    current_data: Union[str, Dict[str, Any]]
    action_taken: str
    next_action: str
    custom_instruction: str
    goal: str
    progress: str

class MotivationResponse(BaseModel):
    prompt: str
    web_results: List[Dict[str, str]]
    youtube_videos: List[Dict[str, str]]
