# src/tools/search_web.py

from ddgs import DDGS

def search_web(query: str, max_results=3):
    """DuckDuckGo search (English only) - enhanced for Agents SDK."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, safesearch='Moderate', timelimit='y', max_results=max_results)
            results = list(results)
        if not results:
            return []
        return [{"title": r["title"], "url": r["href"]} for r in results[:max_results]]
    except Exception as e:
        print(f"Web search error: {e}")
        return [{"title": "Search temporarily unavailable", "url": ""}]
