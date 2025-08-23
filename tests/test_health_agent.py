# tests/test_health_agent.py

import pytest
from src.agents.health_agent import run_health_agent
from src.models.health_models import MotivationRequest, MotivationResponse

@pytest.mark.asyncio
async def test_health_agent_run_real_apis():
    """
    Run agent using real DuckDuckGo + YouTube searches.
    Returns motivational text + top 3 web articles + top 3 YouTube videos.
    """

    # Sample MotivationRequest
    sample_request = MotivationRequest(
        user_id="user123",
        previous_data="Walked 3,000 steps yesterday",
        current_data="Walked 6,000 steps today",
        action_taken="Added an extra workout session",
        next_action="Maintain 7,000+ steps tomorrow",
        custom_instruction="Keep motivation high and suggest healthy recipes",
        goal="Lose 5kg in 2 months",
        progress="I doubled my steps today and added an extra workout!"
    )

    # Run the health agent
    result: MotivationResponse = await run_health_agent(sample_request)

    # Print results for visibility
    print("\n========== MOTIVATION TEXT ==========")
    print(result.prompt)
    print("====================================\n")

    print("---------- Top 3 Web Results ---------")
    for r in result.web_results:
        print(f"{r['title']} -> {r['url']}")
    print("-------------------------------------\n")

    print("-------- Top 3 YouTube Results -------")
    for v in result.youtube_videos:
        print(f"{v['title']} -> {v['url']}")
    print("-------------------------------------\n")

    # ---------------- Basic assertions ----------------
    assert isinstance(result, MotivationResponse)
    assert isinstance(result.prompt, str) and len(result.prompt) > 10
    assert len(result.web_results) == 3
    assert all("title" in r and "url" in r for r in result.web_results)
    assert len(result.youtube_videos) == 3
    assert all("title" in v and "url" in v for v in result.youtube_videos)
