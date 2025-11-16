import pytest
import sys
from src.agents.web_search_agent import WebSearchAgent
from src.models.agent_models import WebSearchRequest
from src.tools.apple_health_kit_mock import AppleHealthKitMock


def _safe(s: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="ignore").decode(enc, errors="ignore")
    except Exception:
        return s


@pytest.mark.asyncio
async def test_web_agent_search():
    web_agent = WebSearchAgent()
    hk = AppleHealthKitMock()

    current = hk.generate_health_data("web_user", 0, "progress")
    previous = hk.generate_health_data("web_user", 1, "normal")

    health = {
        "user_id": "web_user",
        "current_data": current,
        "previous_data": previous,
        "goals": ["Lose 5kg in 2 months"],
        "preferences": {"focus": "sustainable habits"},
    }
    planning_context = {"topic": "Meal Plan", "tone": "Sama"}

    web_req = WebSearchRequest(
        user_id="web_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Find helpful content",
        search_query="healthy meal plan tips beginner",
        max_results=3,
        search_type="general",
    )

    web_res = await web_agent.search_web(web_req)

    print("\n===== WEB AGENT RESULTS =====")
    print(f"Success: {web_res.success}")
    print(f"Count: {len(web_res.results)}")
    if web_res.results:
        first = web_res.results[0]
        print(_safe(f"First: {first.title} - {first.url}"))

    assert web_res.success
    assert len(web_res.results) >= 0

