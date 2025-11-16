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

JUDGE_PROMPT = """Evaluate relevance of resources (0..1):
- Do top results align with the query context?
- Are sources reputable? (prefer medical/recognized sources)
- Are videos informative and aligned with context?
Return ONLY JSON: {"score": <0..1>, "notes": "<why>"}"""


async def evaluate_case(client: OpenAI, case: Dict[str, Any]) -> Dict[str, Any]:
    coord = HealthCoordinator()
    hk = AppleHealthKitMock()
    current = hk.generate_health_data(f"res_{case['id']}", 0, "progress")
    previous = hk.generate_health_data(f"res_{case['id']}", 1, "normal")

    health_data = {
        "user_id": f"res_{case['id']}",
        "current_data": current,
        "previous_data": previous,
        "goals": [case.get("query_context", "")],
    }

    result = await coord.process_health_request(
        user_id=health_data["user_id"],
        health_data=health_data,
        custom_instruction="Focus on relevant, reputable resources."
    )

    web = [{"title": r.title, "url": r.url} for r in (result.web_results.results if result.web_results and result.web_results.success else [])][:3]
    yt = [{"title": v.title, "url": v.url} for v in (result.youtube_results.videos if result.youtube_results and result.youtube_results.success else [])][:3]

    payload = {
        "query_context": case["query_context"],
        "success_criteria": case.get("success_criteria", []),
        "web_top": web,
        "youtube_top": yt
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
    with open("datasets/resources.jsonl","r",encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]

    results: List[Dict[str, Any]] = []
    for c in cases:
        results.append(await evaluate_case(client, c))
    avg = sum(r["score"] for r in results) / max(1, len(results))
    print(json.dumps({"eval":"resources_relevance","average":avg,"results":results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

