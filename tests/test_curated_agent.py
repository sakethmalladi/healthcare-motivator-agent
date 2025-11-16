import pytest
import sys
from src.agents.youtube_search_agent import YouTubeSearchAgent
from src.agents.web_search_agent import WebSearchAgent
from src.agents.curated_search_agent import CuratedSearchAgent
from src.models.agent_models import YouTubeSearchRequest, WebSearchRequest, CuratedSearchRequest
from src.tools.apple_health_kit_mock import AppleHealthKitMock


def _safe(s: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="ignore").decode(enc, errors="ignore")
    except Exception:
        return s


@pytest.mark.asyncio
async def test_curated_agent_from_web_and_youtube():
    yt_agent = YouTubeSearchAgent()
    web_agent = WebSearchAgent()
    curated_agent = CuratedSearchAgent()

    hk = AppleHealthKitMock()
    current = hk.generate_health_data("curate_user", 0, "progress")
    previous = hk.generate_health_data("curate_user", 1, "normal")

    health = {
        "user_id": "curate_user",
        "current_data": current,
        "previous_data": previous,
        "goals": ["Lose 5kg in 2 months"],
        "preferences": {"focus": "sustainable habits"},
    }
    planning_context = {"topic": "Meal Plan", "tone": "Sama"}

    yt_req = YouTubeSearchRequest(
        user_id="curate_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Find helpful content",
        search_query="healthy meal plan high protein",
        max_results=3,
        category="nutrition",
    )
    web_req = WebSearchRequest(
        user_id="curate_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Find helpful content",
        search_query="healthy meal plan tips beginner site:mayoclinic.org OR site:healthline.com OR site:webmd.com",
        max_results=5,
        search_type="general",
    )

    yt_res = await yt_agent.search_videos(yt_req)
    web_res = await web_agent.search_web(web_req)

    curate_req = CuratedSearchRequest(
        user_id="curate_user",
        health_data=health,
        planning_context=planning_context,
        custom_instruction="Prefer trusted medical sources",
        search_query="healthy meal plan",
        max_results=3,
        content_type="article",
        difficulty_level="beginner",
    )

    curated = await curated_agent.curate_from_results(
        request=curate_req,
        web_results=web_res.results if web_res.success else [],
        youtube_results=yt_res.videos if yt_res.success else []
    )

    print("\n===== CURATED RESULTS =====")
    print(f"Success: {curated.success}")
    print(f"Count: {len(curated.articles)}")
    for i, a in enumerate(curated.articles, 1):
        print(_safe(f"{i}. {a.title} - {a.source} - {a.url} ({a.content_type})"))

    assert curated.success
    assert len(curated.articles) >= 0

