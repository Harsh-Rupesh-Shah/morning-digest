"""Finance News Researcher agent extracting 3 Indian and 2 Global macro stories."""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from digest.config import GEMINI_API_KEY, RESEARCHER_MODEL
from digest.search import search_news_24h
from digest.logger import logger
from digest.agents.state import DigestState


def research_finance(state: DigestState) -> DigestState:
    """Gather and extract 3 Indian market stories and 2 global/macro stories from last 24h."""
    logger.info("[AGENT: Finance Researcher] Starting finance news research...")

    # 1. Indian market stories (Sensex, Nifty, RBI)
    indian_articles = search_news_24h("India stock market Sensex Nifty RBI economy news", max_results=6)

    # 2. Global and macroeconomic stories
    global_articles = search_news_24h("global markets inflation federal reserve macroeconomic news", max_results=5)

    indian_context = "\n\n".join(
        f"Indian Story {i+1}:\nTitle: {a['title']}\nSnippet: {a['snippet']}\nURL: {a['url']}"
        for i, a in enumerate(indian_articles)
    )

    global_context = "\n\n".join(
        f"Global Story {i+1}:\nTitle: {a['title']}\nSnippet: {a['snippet']}\nURL: {a['url']}"
        for i, a in enumerate(global_articles)
    )

    prompt = (
        "You are an objective financial news reporter. Based ONLY on the provided articles below, "
        "extract finance headlines from the past 24 hours.\n"
        "Strict rules:\n"
        "1. Extract exactly THREE Indian market stories (focusing on Sensex, Nifty, or RBI).\n"
        "2. Extract exactly TWO Global and macroeconomic stories.\n"
        "3. Every headline must be ONE single concise sentence.\n"
        "4. Strictly report facts only; absolutely NO financial, investment, or buy/sell advice.\n"
        "5. Attach the exact URL from the corresponding article.\n"
        "6. If fewer stories are available, return only the good ones without padding.\n"
        "7. Respond in valid JSON format: a list of exactly 5 objects (or fewer if unavailable) "
        "with 'headline' and 'url' keys. Put the 3 Indian stories first, followed by the 2 Global stories.\n\n"
        f"Indian Market Articles:\n{indian_context}\n\n"
        f"Global Macro Articles:\n{global_context}\n\n"
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
        logger.error(f"[AGENT: Finance Researcher] JSON parsing failed: {e}")
        headlines = []

    logger.info(f"[AGENT: Finance Researcher] Extracted {len(headlines)} headlines.")
    return {
        "finance_headlines": headlines,
        "finance_indian_raw": indian_articles,
        "finance_global_raw": global_articles
    }

