from typing import List, Dict, Any
from src.models.agent_models import CuratedArticle

TRUSTED_SOURCES = [
    "mayoclinic.org",
    "webmd.com",
    "healthline.com",
    "medicalnewstoday.com",
    "pubmed.ncbi.nlm.nih.gov",
    "nutrition.org",
    "acsm.org",
    "acefitness.org",
    "nasm.org",
    "precisionnutrition.com"
]


def _domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return "unknown"


def curate_from_sources(web_results: List[Any], youtube_results: List[Any], planning_context: Dict[str, Any], max_results: int = 3) -> List[CuratedArticle]:
    curated: List[CuratedArticle] = []

    # Web first: filter by trusted sources
    for r in web_results:
        url = getattr(r, "url", None) or (r.get("url") if isinstance(r, dict) else "")
        title = getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else "")
        snippet = getattr(r, "snippet", None) or (r.get("snippet") if isinstance(r, dict) else None)
        if not url:
            continue
        dom = _domain(url)
        if any(s in url.lower() for s in TRUSTED_SOURCES):
            curated.append(CuratedArticle(
                title=title or dom,
                url=url,
                source=dom,
                author=None,
                publish_date=None,
                summary=snippet,
                content_type="article",
                difficulty_level="intermediate"
            ))
            if len(curated) >= max_results:
                return curated

    # Fill with YouTube results if needed
    remaining = max_results - len(curated)
    if remaining > 0:
        for v in youtube_results[:remaining]:
            url = getattr(v, "url", None) or (v.get("url") if isinstance(v, dict) else "")
            title = getattr(v, "title", None) or (v.get("title") if isinstance(v, dict) else "")
            channel = getattr(v, "channel", None) or (v.get("channel") if isinstance(v, dict) else None)
            description = getattr(v, "description", None) or (v.get("description") if isinstance(v, dict) else None)
            if not url:
                continue
            curated.append(CuratedArticle(
                title=title or "YouTube Video",
                url=url,
                source="youtube.com",
                author=channel,
                publish_date=None,
                summary=description,
                content_type="video",
                difficulty_level="intermediate"
            ))
            if len(curated) >= max_results:
                break

    return curated

