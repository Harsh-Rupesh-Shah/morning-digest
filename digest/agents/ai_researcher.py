"""AI News Researcher agent extracting 5 AI headlines from last 24h."""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from digest.config import GEMINI_API_KEY, RESEARCHER_MODEL
from digest.search import search_news_24h
from digest.logger import logger
from digest.agents.state import DigestState


def research_ai(state: DigestState) -> DigestState:
    """Gather and extract top 5 AI headlines from the past 24 hours."""
    logger.info("[AGENT: AI Researcher] Starting AI news research...")

    # Fetch articles from last 24h
    articles = search_news_24h("AI artificial intelligence machine learning news breakthroughs", max_results=8)
    if not articles:
        articles = search_news_24h("Generative AI LLM research news", max_results=5)

    if not articles:
        logger.warning("[AGENT: AI Researcher] No AI articles fetched.")
        return {"ai_headlines": []}

    context = "\n\n".join(
        f"Article {i+1}:\nTitle: {a['title']}\nSnippet: {a['snippet']}\nURL: {a['url']}"
        for i, a in enumerate(articles)
    )

    prompt = (
        "You are an objective AI news researcher. Based ONLY on the provided articles below, "
        "extract up to 5 of the most important AI headlines from the past 24 hours.\n"
        "Strict rules:\n"
        "1. Every headline must be exactly ONE concise sentence summarizing what happened.\n"
        "2. Do NOT use your own memory; only use facts from the provided text.\n"
        "3. Attach the exact URL from the corresponding article.\n"
        "4. If there are fewer than 5 valid, non-redundant stories, return only the good ones without padding.\n"
        "5. Respond in valid JSON format: a list of objects with 'headline' and 'url' keys.\n\n"
        f"Articles:\n{context}\n\n"
        "JSON Response:"
    )

    llm = ChatGoogleGenerativeAI(model=RESEARCHER_MODEL, api_key=GEMINI_API_KEY, temperature=0.1)
    response = llm.invoke(prompt)

    try:
        raw_text = response.content.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
        headlines = json.loads(raw_text)
    except Exception as e:
        logger.error(f"[AGENT: AI Researcher] JSON parsing failed: {e}")
        headlines = []

    logger.info(f"[AGENT: AI Researcher] Extracted {len(headlines)} headlines.")
    return {"ai_headlines": headlines, "ai_raw_articles": articles}

