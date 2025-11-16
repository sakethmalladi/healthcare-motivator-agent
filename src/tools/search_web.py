# src/tools/search_web.py

import os
from ddgs import DDGS
from typing import List, Dict
from openai import OpenAI


def _search_with_openai(query: str, max_results: int) -> List[Dict[str, str]]:
    """
    Attempt to use OpenAI's web search tool via Responses API.
    Falls back to DDG if unavailable or parsing fails.
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Prompt the model to perform a web search and return N links with titles
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=f"Search the web and return the top {max_results} links with titles for: {query}. "
                  f'Return as lines in the form "Title - URL".',
            tools=[{"type": "web_search"}],
        )
        # Extract text
        text = ""
        try:
            text = resp.output_text  # recent SDK convenience
        except Exception:
            # Fallback parse
            if resp.output and len(resp.output) > 0 and hasattr(resp.output[0], "content"):
                text = "".join([c.text for c in getattr(resp.output[0], "content", []) if hasattr(c, "text")])
        if not text:
            raise RuntimeError("Empty OpenAI web search response")
        results: List[Dict[str, str]] = []
        for line in text.splitlines():
            if " - " in line:
                title, url = line.split(" - ", 1)
                title = title.strip().strip("-").strip()
                url = url.strip()
                if url:
                    results.append({"title": title, "url": url})
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        print(f"OpenAI web search failed, falling back to DDG: {e}")
        return []


def search_web(query: str, max_results=3):
    """Web search preferring OpenAI's web tool, with DDG fallback."""
    # Try OpenAI web tool first
    results = _search_with_openai(query, max_results)
    if results:
        return results[:max_results]

    # Fallback to DuckDuckGo
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, safesearch='Moderate', timelimit='y', max_results=max_results)
            results = list(results)
        if not results:
            return []
        return [{"title": r.get("title", ""), "url": r.get("href", "")} for r in results[:max_results]]
    except Exception as e:
        print(f"Web search error: {e}")
        return [{"title": "Search temporarily unavailable", "url": ""}]
