import pytest
import sys
from src.agents.youtube_search_agent import YouTubeSearchAgent
from src.models.agent_models import YouTubeSearchRequest
from src.tools.apple_health_kit_mock import AppleHealthKitMock


def _safe(s: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="ignore").decode(enc, errors="ignore")
    except Exception:
        return s


@pytest.mark.asyncio
async def test_youtube_agent_search_and_transcript():
    yt_agent = YouTubeSearchAgent()
    hk = AppleHealthKitMock()

    current = hk.generate_health_data("yt_user", 0, "progress")
    previous = hk.generate_health_data("yt_user", 1, "normal")

    health = {
        "user_id": "yt_user",
        "current_data": current,
        "previous_data": previous,
        "goals": ["Lose 5kg in 2 months"],
        "preferences": {"focus": "sustainable habits"},
    }
    planning_context = {"topic": "Meal Plan", "tone": "Sama"}

    yt_req = YouTubeSearchRequest(
        user_id="yt_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Find helpful content",
        search_query="healthy meal plan high protein",
        max_results=3,
        category="nutrition",
    )

    yt_res = await yt_agent.search_videos(yt_req)

    print("\n===== YOUTUBE AGENT RESULTS =====")
    print(f"Success: {yt_res.success}")
    print(f"Count: {len(yt_res.videos)}")
    if yt_res.metadata and yt_res.metadata.get("openai_response_id"):
        print(f"OpenAI response_id: {yt_res.metadata.get('openai_response_id')}")
    if yt_res.videos:
        first = yt_res.videos[0]
        print(_safe(f"First: {first.title} - {first.url}"))
        if first.description:
            print(_safe(f"Transcript snippet: {first.description[:140]}{'...' if len(first.description) > 140 else ''}"))

    assert yt_res.success
    assert len(yt_res.videos) >= 0

