import pytest
import sys
from src.agents.health_coordinator import HealthCoordinator
from src.tools.apple_health_kit_mock import AppleHealthKitMock


def _safe(s: str) -> str:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        return s.encode(enc, errors="ignore").decode(enc, errors="ignore")
    except Exception:
        return s


@pytest.mark.asyncio
async def test_end_to_end_simple():
    """Minimal end-to-end test with sample input and step-by-step outputs."""
    coordinator = HealthCoordinator()
    hk = AppleHealthKitMock()

    # Sample input (simple, single scenario)
    current_data = hk.generate_health_data("user_simple", 0, "progress")
    previous_data = hk.generate_health_data("user_simple", 1, "normal")
    sample = {
        "user_id": "user_simple",
        "current_data": current_data,
        "previous_data": previous_data,
        "goals": ["Lose 5kg in 2 months"],
        "preferences": {"focus": "sustainable habits"},
        "mood": "motivated",
        "energy_level": 7,
        "challenges": ["evening snacking"],
        "achievements": ["Walked 7,500 steps today"]
    }

    # Run complete project flow
    result = await coordinator.process_health_request(
        user_id=sample["user_id"],
        health_data=sample,
        custom_instruction="Keep it simple and sustainable"
    )

    # Minimal prints and assertions
    print("\n===== RESULT =====")
    assert result.planning_decision is not None
    print(f"Planning: {result.planning_decision.tone} for {result.planning_decision.topic}")

    # Print OpenAI response IDs to help locate logs in dashboard
    try:
        planning_meta = (result.metadata or {}).get("planning", {})
        pm = planning_meta.get("metadata", {}) if planning_meta else {}
        planning_resp_id = pm.get("openai_response_id")
        if planning_resp_id:
            print(f"Planning OpenAI response_id: {planning_resp_id}")
    except Exception:
        pass
    try:
        if result.curated_results and result.curated_results.metadata:
            curated_resp_id = result.curated_results.metadata.get("openai_response_id")
            if curated_resp_id:
                print(f"Curated OpenAI response_id: {curated_resp_id}")
    except Exception:
        pass

    assert isinstance(result.overall_summary, str) and len(result.overall_summary) > 0
    print(_safe(result.overall_summary[:200] + ("..." if len(result.overall_summary) > 200 else "")))
