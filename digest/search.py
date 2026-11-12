"""Web search service with 24-hour news filtering and search tracking."""

from typing import List, Dict
from digest.config import TAVILY_API_KEY
from digest.logger import logger, record_search


def search_news_24h(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search for news published in the last 24 hours with source links.

    Uses Tavily Search API with automatic DuckDuckGo fallback.
    """
    record_search()
    logger.info(f"[SEARCH] Querying news (last 24h): '{query}' (limit: {max_results})")

    # 1. Try Tavily Search API
    if TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=TAVILY_API_KEY)
            response = client.search(
                query=query,
                topic="news",
                days=1,
                max_results=max_results
            )
            raw_results = response.get("results", [])
            articles = []
            for item in raw_results:
                title = item.get("title", "").strip()
                url = item.get("url", "").strip()
                snippet = item.get("content", "").strip()
                if title and url:
                    articles.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
            if articles:
                logger.info(f"[SEARCH] Tavily returned {len(articles)} articles.")
                return articles
        except Exception as e:
            logger.warning(f"[SEARCH] Tavily search error: {e}. Attempting fallback.")

    # 2. Fallback: DuckDuckGo News
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.news(query, timelimit="d", max_results=max_results))
            articles = []
            for item in raw:
                title = item.get("title", "").strip()
                url = item.get("url", "").strip()
                snippet = item.get("body", "").strip()
                if title and url:
                    articles.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
            logger.info(f"[SEARCH] DuckDuckGo returned {len(articles)} articles.")
            return articles
    except Exception as e:
        logger.error(f"[SEARCH] DuckDuckGo fallback failed: {e}")
        return []

