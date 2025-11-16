import pytest
import sys
from src.agents.planning_agent import PlanningAgent
from src.models.agent_models import PlanningRequest
from src.tools.apple_health_kit_mock import AppleHealthKitMock


def _safe(s: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="ignore").decode(enc, errors="ignore")
    except Exception:
        return s


@pytest.mark.asyncio
async def test_planning_agent_creates_decision():
    """Direct test for PlanningAgent.create_plan with sample health data."""
    agent = PlanningAgent()
    hk = AppleHealthKitMock()

    current_data = hk.generate_health_data("planner_user", 0, "progress")
    previous_data = hk.generate_health_data("planner_user", 1, "normal")

    sample = {
        "user_id": "planner_user",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Lose 5kg in 2 months"],
        "preferences": {"focus": "sustainable habits"},
        "mood": "motivated",
        "energy_level": 7,
        "challenges": ["evening snacking"],
        "achievements": ["Walked 7,500 steps today"]
    }

    request = PlanningRequest(
        user_id=sample["user_id"],
        health_data=sample,
        health_analysis={"current_data": current_data, "previous_data": previous_data},
        user_goals=sample["goals"],
        user_preferences=sample["preferences"],
        custom_instruction="Keep it simple and sustainable"
    )

    response = await agent.create_plan(request)

    print("\n===== PLANNING AGENT RESULT =====")
    print(f"Success: {response.success}")
    print(f"Theme: {response.decision.theme}")
    print(f"Topic: {response.decision.topic}")
    print(f"Tone: {response.decision.tone}")
    print(f"Confidence: {response.decision.confidence_score}")
    meta = response.metadata or {}
    raw = meta.get("raw_llm_response")
    if raw:
        print("\n--- Raw LLM Planning Response (truncated) ---")
        print(_safe(raw[:500] + ("..." if len(raw) > 500 else "")))

    assert response.decision is not None
    assert isinstance(response.decision.theme, str) and len(response.decision.theme) > 0
    assert isinstance(response.decision.topic, str) and len(response.decision.topic) > 0
    assert isinstance(response.decision.tone, str) and len(response.decision.tone) > 0
    assert 0.0 <= float(response.decision.confidence_score) <= 1.0

