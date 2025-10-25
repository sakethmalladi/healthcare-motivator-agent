# src/tools/search_youtube.py

def search_youtube(query: str) -> list[str]:
    """YouTube search function - enhanced error handling for Agents SDK."""
    try:
        from youtubesearchpython import VideosSearch
        results = []
        videos_search = VideosSearch(query, limit=3)
        for v in videos_search.result()["result"]:
            results.append(v["title"] + " - " + v["link"])
        return results
    except ImportError:
        print("youtube-search-python not installed. Run: pip install youtube-search-python")
        return ["YouTube search unavailable - missing dependency - https://youtube.com"]
    except Exception as e:
        print(f"YouTube search error: {e}")
        return [f"YouTube search error: {str(e)} - https://youtube.com"]
