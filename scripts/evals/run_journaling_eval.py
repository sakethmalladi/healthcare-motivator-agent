import asyncio
import json
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

JUDGE_MODEL = "gpt-4o-mini"

JUDGE_PROMPT = """Evaluate journal usefulness (0..1):
- Empathetic and aligned with mood/context.
- Provides actionable next steps.
- Reinforces user's goals.
Return ONLY JSON: {"score": <0..1>, "notes": "<why>"}"""


async def evaluate_case(client: OpenAI, case: Dict[str, Any]) -> Dict[str, Any]:
    coord = HealthCoordinator()
    hk = AppleHealthKitMock()
    current = hk.generate_health_data(f"jr_{case['id']}", 0, "progress")
    previous = hk.generate_health_data(f"jr_{case['id']}", 1, "normal")

    health_data = {
        "user_id": f"jr_{case['id']}",
        "current_data": current,
        "previous_data": previous,
        "goals": case.get("user_goals", []),
        "mood": case.get("mood"),
        "energy_level": case.get("energy_level")
    }

    result = await coord.process_health_request(
        user_id=health_data["user_id"],
        health_data=health_data,
        custom_instruction="Produce a supportive journal entry."
    )

    entry = ""
    if result.journaling_results and result.journaling_results.success:
        entry = result.journaling_results.journal_entry.content

    payload = {
        "goals": case.get("user_goals", []),
        "desired_style": case.get("desired_style", []),
        "journal": entry[:1500]
    }

    judge = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
        temperature=0
    )
    text = judge.choices[0].message.content
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = {"score": 0.0, "notes": f"Parse error: {text[:200]}"}

    return {"id": case["id"], "score": float(parsed.get("score", 0.0)), "notes": parsed.get("notes","")}


async def main():
    client = OpenAI()
    with open("datasets/journaling.jsonl","r",encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]
    results: List[Dict[str, Any]] = []
    for c in cases:
        results.append(await evaluate_case(client, c))
    avg = sum(r["score"] for r in results) / max(1, len(results))
    print(json.dumps({"eval":"journaling_usefulness","average":avg,"results":results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

