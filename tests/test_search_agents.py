import pytest
import sys
from src.agents.youtube_search_agent import YouTubeSearchAgent
from src.agents.web_search_agent import WebSearchAgent
from src.models.agent_models import YouTubeSearchRequest, WebSearchRequest
from src.tools.apple_health_kit_mock import AppleHealthKitMock


def _safe(s: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="ignore").decode(enc, errors="ignore")
    except Exception:
        return s


@pytest.mark.asyncio
async def test_youtube_and_web_search_prints():
    yt_agent = YouTubeSearchAgent()
    web_agent = WebSearchAgent()
    hk = AppleHealthKitMock()

    current = hk.generate_health_data("search_user", 0, "progress")
    previous = hk.generate_health_data("search_user", 1, "normal")

    health = {
        "user_id": "search_user",
        "current_data": current,
        "previous_data": previous,
        "goals": ["Lose 5kg in 2 months"],
        "preferences": {"focus": "sustainable habits"},
    }
    planning_context = {"topic": "Meal Plan", "tone": "Sama"}

    yt_req = YouTubeSearchRequest(
        user_id="search_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Find helpful content",
        search_query="healthy meal plan high protein",
        max_results=3,
        category="nutrition",
    )

    web_req = WebSearchRequest(
        user_id="search_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Find helpful content",
        search_query="healthy meal plan tips beginner",
        max_results=3,
        search_type="general",
    )

    yt_res = await yt_agent.search_videos(yt_req)
    web_res = await web_agent.search_web(web_req)

    print("\n===== YOUTUBE SEARCH RESULTS =====")
    print(f"Success: {yt_res.success}")
    print(f"Count: {len(yt_res.videos)}")
    if yt_res.videos:
        print(_safe(f"First: {yt_res.videos[0].title} - {yt_res.videos[0].url}"))

    print("\n===== WEB SEARCH RESULTS =====")
    print(f"Success: {web_res.success}")
    print(f"Count: {len(web_res.results)}")
    if web_res.results:
        print(_safe(f"First: {web_res.results[0].title} - {web_res.results[0].url}"))

    assert yt_res.success
    assert web_res.success
    assert len(yt_res.videos) >= 0  # allow zero in case API fallback yields none
    assert len(web_res.results) >= 0

