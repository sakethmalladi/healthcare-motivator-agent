import os
import pytest
from src.agents.health_agent import run_health_agent
from src.models.health_models import MotivationRequest, MotivationResponse

@pytest.mark.asyncio
async def test_health_agent_run_real_apis():
    """
    Run the motivation agent using real DuckDuckGo + YouTube searches (local mode),
    or via OpenAI Agents SDK if MOTIVATE_AGENT_ID is set.
    Validates that it returns motivational text + results.
    """

    # Sample MotivationRequest
    sample_request = MotivationRequest(
        user_id="user123",
        previous_data={"steps": 3000, "calories": 1800, "workouts": 1, "weight": 75, "goal_steps": 7000},
        current_data={"steps": 6000, "calories": 2000, "workouts": 2, "weight": 74.5, "goal_steps": 7000},
        action_taken="Added an extra workout session",
        next_action="Maintain 7,000+ steps tomorrow",
        custom_instruction="Keep motivation high and suggest healthy recipes",
        goal="Lose 5kg in 2 months",
        progress="compliant"
    )

    # Run the health agent (SDK mode if MOTIVATE_AGENT_ID is set, else local mode)
    result: MotivationResponse = await run_health_agent(sample_request)

    # Print results for visibility
    print("\n========== MOTIVATION TEXT ==========")
    print(result.prompt)
    print("====================================\n")

    if os.getenv("MOTIVATE_AGENT_ID"):
        # In SDK mode, we don’t have tool outputs
        assert isinstance(result.prompt, str)
        assert len(result.prompt) > 20
        assert result.web_results == []
        assert result.youtube_videos == []
    else:
        # Local mode should return tools output
        print("---------- Top 3 Web Results ---------")
        for r in result.web_results:
            print(f"{r['title']} -> {r['url']}")
        print("-------------------------------------\n")

        print("-------- Top 3 YouTube Results -------")
        for v in result.youtube_videos:
            print(f"{v['title']} -> {v['url']}")
        print("-------------------------------------\n")

        assert isinstance(result.prompt, str) and len(result.prompt) > 20
        assert len(result.web_results) == 3
        assert all("title" in r and "url" in r for r in result.web_results)
        assert len(result.youtube_videos) == 3
        assert all("title" in v and "url" in v for v in result.youtube_videos)
