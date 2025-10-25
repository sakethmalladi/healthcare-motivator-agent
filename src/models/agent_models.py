# src/models/agent_models.py

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    YOUTUBE_SEARCH = "youtube_search"
    CURATED_SEARCH = "curated_search"
    WEB_SEARCH = "web_search"
    JOURNALING = "journaling"
    PLANNING = "planning"

class AgentRequest(BaseModel):
    """Base request model for all agents"""
    user_id: str
    health_data: Dict[str, Any]
    planning_context: Optional[Dict[str, Any]] = None
    custom_instruction: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentResponse(BaseModel):
    """Base response model for all agents"""
    agent_type: AgentType
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# YouTube Search Agent Models
class YouTubeSearchRequest(AgentRequest):
    """Request model for YouTube Search Agent"""
    search_query: str
    max_results: int = 3
    video_duration: Optional[str] = None  # "short", "medium", "long"
    category: Optional[str] = None  # "fitness", "nutrition", "motivation"

class YouTubeVideo(BaseModel):
    """Individual YouTube video result"""
    title: str
    url: str
    duration: Optional[str] = None
    views: Optional[str] = None
    channel: Optional[str] = None
    description: Optional[str] = None

class YouTubeSearchResponse(AgentResponse):
    """Response model for YouTube Search Agent"""
    agent_type: AgentType = AgentType.YOUTUBE_SEARCH
    videos: List[YouTubeVideo] = Field(default_factory=list)
    search_query_used: str = ""

# Curated Search Agent Models
class CuratedSearchRequest(AgentRequest):
    """Request model for Curated Search Agent"""
    search_query: str
    max_results: int = 3
    content_type: Optional[str] = None  # "article", "study", "guide", "recipe"
    difficulty_level: Optional[str] = None  # "beginner", "intermediate", "advanced"

class CuratedArticle(BaseModel):
    """Individual curated article result"""
    title: str
    url: str
    source: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    summary: Optional[str] = None
    content_type: str = "article"
    difficulty_level: str = "intermediate"

class CuratedSearchResponse(AgentResponse):
    """Response model for Curated Search Agent"""
    agent_type: AgentType = AgentType.CURATED_SEARCH
    articles: List[CuratedArticle] = Field(default_factory=list)
    search_query_used: str = ""

# Web Search Agent Models
class WebSearchRequest(AgentRequest):
    """Request model for Web Search Agent"""
    search_query: str
    max_results: int = 3
    search_type: Optional[str] = None  # "general", "news", "academic", "forum"

class WebResult(BaseModel):
    """Individual web search result"""
    title: str
    url: str
    snippet: Optional[str] = None
    source: Optional[str] = None
    publish_date: Optional[str] = None

class WebSearchResponse(AgentResponse):
    """Response model for Web Search Agent"""
    agent_type: AgentType = AgentType.WEB_SEARCH
    results: List[WebResult] = Field(default_factory=list)
    search_query_used: str = ""

# Journaling Agent Models
class JournalingRequest(AgentRequest):
    """Request model for Journaling Agent"""
    journal_type: str  # "daily_reflection", "progress_update", "goal_setting", "struggle_support"
    previous_entry: Optional[str] = None
    mood: Optional[str] = None
    energy_level: Optional[int] = None  # 1-10 scale
    challenges_faced: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

class JournalEntry(BaseModel):
    """Individual journal entry"""
    entry_id: str
    entry_type: str
    content: str
    mood: Optional[str] = None
    energy_level: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)

class JournalingResponse(AgentResponse):
    """Response model for Journaling Agent"""
    agent_type: AgentType = AgentType.JOURNALING
    journal_entry: JournalEntry
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    next_journal_prompt: Optional[str] = None

# Planning Agent Models
class PlanningRequest(AgentRequest):
    """Request model for Planning Agent"""
    health_analysis: Dict[str, Any]
    user_goals: List[str] = Field(default_factory=list)
    user_preferences: Optional[Dict[str, Any]] = None

class PlanningDecision(BaseModel):
    """Planning decision from AI Planning Agent"""
    theme: str
    topic: str
    tone: str
    tone_description: str
    tone_characteristics: List[str]
    timing: Dict[str, Any]
    reasoning: str
    confidence_score: float  # 0-1

class PlanningResponse(AgentResponse):
    """Response model for Planning Agent"""
    agent_type: AgentType = AgentType.PLANNING
    decision: PlanningDecision
    context_for_other_agents: Dict[str, Any] = Field(default_factory=dict)

# Coordinated Response Model
class CoordinatedResponse(BaseModel):
    """Combined response from all agents"""
    user_id: str
    planning_decision: PlanningDecision
    youtube_results: Optional[YouTubeSearchResponse] = None
    curated_results: Optional[CuratedSearchResponse] = None
    web_results: Optional[WebSearchResponse] = None
    journaling_results: Optional[JournalingResponse] = None
    overall_summary: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
