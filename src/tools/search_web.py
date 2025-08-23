from ddgs import DDGS

def search_web(query: str, max_results=3):
    """DuckDuckGo search (English only)."""
    with DDGS() as ddgs:
        results = ddgs.text(query, safesearch='Moderate', timelimit='y', max_results=max_results)
        results = list(results)
    if not results:
        return []
    return [{"title": r["title"], "url": r["href"]} for r in results[:max_results]]
