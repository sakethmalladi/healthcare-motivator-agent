import asyncio
import json
import os
from typing import Dict, Any, List
from openai import OpenAI
import sys
from pathlib import Path

# Ensure project root on sys.path for 'src' imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.health_coordinator import HealthCoordinator
from src.tools.apple_health_kit_mock import AppleHealthKitMock

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-4o-mini")

JUDGE_PROMPT = """You are a strict evaluator. Score the planning decision (0..1) against the rubric.
Criteria:
- Topic matches the user's needs and context.
- Reasoning addresses the user's challenges.
- Timing is reasonable for the context.
Return ONLY JSON: {"score": <0..1>, "notes": "<why>"}"""


async def evaluate_case(client: OpenAI, case: Dict[str, Any]) -> Dict[str, Any]:
    coord = HealthCoordinator()
    hk = AppleHealthKitMock()
    current = hk.generate_health_data(f"eval_{case['id']}", 0, "progress")
    previous = hk.generate_health_data(f"eval_{case['id']}", 1, "normal")

    health_data = {
        "user_id": f"eval_{case['id']}",
        "current_data": current,
        "previous_data": previous,
        "goals": case.get("user_goals", []),
        "mood": case.get("mood"),
        "energy_level": case.get("energy_level"),
        "challenges": case.get("challenges", [])
    }

    result = await coord.process_health_request(
        user_id=health_data["user_id"],
        health_data=health_data,
        custom_instruction="Please plan appropriately."
    )

    plan = result.planning_decision
    planning_json = {
        "theme": plan.theme,
        "topic": plan.topic,
        "timing": plan.timing,
        "reasoning": plan.reasoning
    }
    rubric = {
        "expected_topic": case.get("expected_topic"),
        "success_criteria": case.get("expected_success_criteria", [])
    }

    judge_input = f"RUBRIC:\n{json.dumps(rubric, ensure_ascii=False)}\n\nPLAN:\n{json.dumps(planning_json, ensure_ascii=False)}"
    judge = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": judge_input}
        ],
        temperature=0
    )

    text = judge.choices[0].message.content
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = {"score": 0.0, "notes": f"Parse error: {text[:200]}"}

    return {
        "id": case["id"],
        "topic": plan.topic,
        "score": float(parsed.get("score", 0.0)),
        "notes": parsed.get("notes", "")
    }


async def main():
    client = OpenAI()
    with open("datasets/planning.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]

    results: List[Dict[str, Any]] = []
    for c in cases:
        results.append(await evaluate_case(client, c))

    avg = sum(r["score"] for r in results) / max(1, len(results))
    output = {"eval": "planning_quality", "average": avg, "results": results}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

