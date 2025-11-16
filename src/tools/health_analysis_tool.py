# src/tools/health_analysis_tool.py

from typing import Dict, Any, Optional
from src.models.health_kit_models import HealthKitData
from src.tools.planning_tool import PlanningTool

_planning_tool_singleton: Optional[PlanningTool] = None


def _get_planning_tool() -> PlanningTool:
    global _planning_tool_singleton
    if _planning_tool_singleton is None:
        _planning_tool_singleton = PlanningTool()
    return _planning_tool_singleton


def analyze_health_score(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Analyze health data and return a structured analysis dict.
    Expected health_data contains 'current_data' and optional 'previous_data' as HealthKitData.
    """
    tool = _get_planning_tool()
    current: HealthKitData = health_data.get("current_data")
    previous: Optional[HealthKitData] = health_data.get("previous_data")
    analysis = tool.analyze_health_data(current, previous)
    return {
        "user_id": analysis.user_id,
        "overall_health_score": analysis.overall_health_score,
        "recommendations": analysis.recommendations,
        "concerns": analysis.concerns,
        "achievements": analysis.achievements,
        "next_goals": analysis.next_goals,
    }


