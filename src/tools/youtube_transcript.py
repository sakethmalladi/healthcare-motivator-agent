from typing import Optional, List, Dict
import re

def _extract_video_id(url_or_id: str) -> str:
    # Simple patterns for common YouTube URLs
    patterns = [
        r"(?:v=)([A-Za-z0-9_\-]{6,})",
        r"youtu\.be/([A-Za-z0-9_\-]{6,})",
        r"youtube\.com/shorts/([A-Za-z0-9_\-]{6,})",
    ]
    for pat in patterns:
        m = re.search(pat, url_or_id)
        if m:
            return m.group(1)
    return url_or_id  # assume already an ID


def get_transcript(url_or_id: str, max_chars: int = 1200, languages: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Fetch a transcript for a YouTube video and return a truncated string.
    Requires: youtube-transcript-api
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
        vid = _extract_video_id(url_or_id)
        languages = languages or ["en", "en-US"]
        transcript_list = YouTubeTranscriptApi.get_transcript(vid, languages=languages)
        text = " ".join(chunk.get("text", "") for chunk in transcript_list if chunk.get("text"))
        if not text:
            return {"status": "empty", "transcript": ""}
        text = text.replace("\n", " ").strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return {"status": "success", "transcript": text}
    except Exception as e:
        return {"status": "error", "transcript": "", "message": str(e)}


