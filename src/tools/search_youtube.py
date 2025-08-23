from youtubesearchpython import VideosSearch

def search_youtube(query: str) -> list[str]:
    """Directly callable YouTube search function (also wrapped for Agent SDK)."""
    results = []
    videos_search = VideosSearch(query, limit=3)
    for v in videos_search.result()["result"]:
        results.append(v["title"] + " - " + v["link"])
    return results
