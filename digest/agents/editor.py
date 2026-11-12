"""Editor agent ensuring deduplication, structure, and mobile-friendly formatting."""

from datetime import datetime
from typing import List, Dict, Any
from digest.logger import logger
from digest.agents.state import DigestState, StoryItem


def _clean_and_deduplicate(stories: List[StoryItem], seen_urls: set) -> List[StoryItem]:
    """Filter out duplicate stories and ensure clean formatting."""
    cleaned = []
    for item in stories:
        url = item.get("url", "").strip()
        headline = item.get("headline", "").strip()
        if not url or not headline:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        cleaned.append({"headline": headline, "url": url})
    return cleaned


def edit_and_format(state: DigestState) -> DigestState:
    """Validate, deduplicate, and assemble the mobile-friendly morning digest."""
    logger.info("[AGENT: Editor] Editing and assembling the morning digest...")

    seen_urls = set()
    ai_stories = _clean_and_deduplicate(state.get("ai_headlines", []), seen_urls)
    tech_stories = _clean_and_deduplicate(state.get("tech_headlines", []), seen_urls)
    finance_stories = _clean_and_deduplicate(state.get("finance_headlines", []), seen_urls)

    date_str = state.get("date") or datetime.now().strftime("%B %d, %Y")

    # Plain text construction
    text_lines = [
        f"MORNING BRIEF — {date_str.upper()}",
        "=" * 45,
        "",
        "🤖 ARTIFICIAL INTELLIGENCE",
        "-" * 30
    ]
    if ai_stories:
        for i, s in enumerate(ai_stories[:5], 1):
            text_lines.append(f"{i}. {s['headline']} ({s['url']})")
    else:
        text_lines.append("(Fewer than 5 stories found today; zero padding added)")

    text_lines.extend(["", "💻 TECHNOLOGY", "-" * 30])
    if tech_stories:
        for i, s in enumerate(tech_stories[:5], 1):
            text_lines.append(f"{i}. {s['headline']} ({s['url']})")
    else:
        text_lines.append("(Fewer than 5 stories found today; zero padding added)")

    text_lines.extend(["", "📈 FINANCE & ECONOMY", "-" * 30])
    if finance_stories:
        for i, s in enumerate(finance_stories[:5], 1):
            text_lines.append(f"{i}. {s['headline']} ({s['url']})")
    else:
        text_lines.append("(Fewer than 5 stories found today; zero padding added)")

    text_lines.extend([
        "",
        "-" * 45,
        "Note: Objective financial facts only. No buy/sell advice.",
        "Generated autonomously by NOVA Morning Digest."
    ])
    plain_text = "\n".join(text_lines)

    # HTML construction optimized for mobile reading
    def make_section_html(title: str, icon: str, stories: List[StoryItem]) -> str:
        items_html = ""
        if not stories:
            items_html = '<li style="color: #6b7280; font-style: italic;">No verified stories found today.</li>'
        else:
            for s in stories[:5]:
                items_html += (
                    '<li style="margin-bottom: 12px; line-height: 1.5; color: #1f2937;">'
                    f'{s["headline"]} '
                    f'<a href="{s["url"]}" style="color: #2563eb; text-decoration: none; font-weight: 500;" target="_blank">[Source]</a>'
                    '</li>'
                )
            if len(stories) < 5:
                items_html += (
                    f'<li style="color: #6b7280; font-style: italic; list-style-type: none; font-size: 13px;">'
                    f'Note: Only {len(stories)} stories verified in the last 24h.</li>'
                )

        return f"""
        <div style="background: #ffffff; border-radius: 12px; padding: 18px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 4px solid #3b82f6;">
            <h2 style="margin: 0 0 14px 0; font-size: 18px; color: #111827; display: flex; align-items: center;">
                <span style="margin-right: 8px;">{icon}</span> {title}
            </h2>
            <ol style="margin: 0; padding-left: 20px; font-size: 15px;">
                {items_html}
            </ol>
        </div>
        """

    ai_html = make_section_html("Artificial Intelligence", "🤖", ai_stories)
    tech_html = make_section_html("Technology", "💻", tech_stories)
    finance_html = make_section_html("Finance & Economy", "📈", finance_stories)

    html_email = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Brief — {date_str}</title>
</head>
<body style="margin: 0; padding: 16px; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto;">
        <!-- Header -->
        <div style="text-align: center; padding: 20px 0 16px 0;">
            <span style="font-size: 12px; font-weight: 700; letter-spacing: 1px; color: #6b7280; text-transform: uppercase;">NOVA Intelligence</span>
            <h1 style="margin: 6px 0 4px 0; font-size: 24px; color: #111827;">Morning Brief</h1>
            <p style="margin: 0; color: #4b5563; font-size: 14px;">{date_str}</p>
        </div>

        <!-- Sections -->
        {ai_html}
        {tech_html}
        {finance_html}

        <!-- Footer -->
        <div style="text-align: center; padding: 16px; font-size: 12px; color: #9ca3af; line-height: 1.4;">
            <p style="margin: 0 0 4px 0;">Objective reporting only • No buy/sell advice</p>
            <p style="margin: 0;">Automated via LangChain Deep Agents on Gemini Flash</p>
        </div>
    </div>
</body>
</html>"""

    logger.info("[AGENT: Editor] Morning digest formatted and ready.")
    return {
        "ai_headlines": ai_stories[:5],
        "tech_headlines": tech_stories[:5],
        "finance_headlines": finance_stories[:5],
        "email_html": html_email,
        "email_text": plain_text
    }

