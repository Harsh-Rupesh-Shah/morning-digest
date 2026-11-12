"""State schema for Morning News Digest multi-agent workflow."""

from typing import List, Dict, Any, TypedDict


class StoryItem(TypedDict):
    headline: str
    url: str


class DigestState(TypedDict, total=False):
    date: str
    ai_raw_articles: List[Dict[str, str]]
    tech_raw_articles: List[Dict[str, str]]
    finance_indian_raw: List[Dict[str, str]]
    finance_global_raw: List[Dict[str, str]]
    ai_headlines: List[StoryItem]
    tech_headlines: List[StoryItem]
    finance_headlines: List[StoryItem]
    email_html: str
    email_text: str
    metrics: Dict[str, Any]

