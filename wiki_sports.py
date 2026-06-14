"""
wiki_sports.py - Wikipedia-Powered Sports Data Engine
======================================================
Fetches sports data from Wikipedia's free API.
No API key needed — unlimited, free access!

Uses smart keyword extraction and multiple search strategies.
"""

import re
import requests
from typing import Dict, List, Optional

WIKI_API = "https://en.wikipedia.org/w/api.php"

# Common question words to strip for better search
QUESTION_WORDS = {"who", "what", "when", "where", "why", "how", "which", "is", "are",
                   "was", "were", "has", "have", "had", "do", "does", "did", "the",
                   "a", "an", "in", "of", "on", "at", "to", "for", "with", "about",
                   "tell", "me", "give", "list", "explain", "describe", "most", "best",
                   "top", "all", "time", "ever", "many", "much"}

# Topic mappings: natural queries → Wikipedia article titles
TOPIC_MAP = {
    "most centuries cricket": "List of international cricket centuries",
    "centuries cricket": "List of international cricket centuries",
    "cricket records": "List of cricket records",
    "cricket world records": "List of cricket records",
    "virat kohli": "Virat Kohli",
    "sachin tendulkar": "Sachin Tendulkar",
    "ms dhoni": "MS Dhoni",
    "rohit sharma": "Rohit Sharma",
    "messi": "Lionel Messi",
    "ronaldo": "Cristiano Ronaldo",
    "messi vs ronaldo": "Lionel Messi and Cristiano Ronaldo rivalry",
    "messi ronaldo": "Lionel Messi and Cristiano Ronaldo rivalry",
    "lebron james": "LeBron James",
    "michael jordan": "Michael Jordan",
    "lebron vs jordan": "LeBron James vs. Michael Jordan",
    "fifa world cup": "FIFA World Cup",
    "fifa world cup 2022": "2022 FIFA World Cup",
    "world cup 2022": "2022 FIFA World Cup",
    "ipl": "Indian Premier League",
    "nba": "National Basketball Association",
    "nba scoring leaders": "List of NBA career scoring leaders",
    "nba all time": "List of NBA career scoring leaders",
    "premier league": "Premier League",
    "champions league": "UEFA Champions League",
    "grand slam tennis": "Grand Slam (tennis)",
    "wimbledon": "The Championships, Wimbledon",
    "formula 1": "Formula One",
    "f1 champions": "List of Formula One World Drivers' Champions",
    "f1 drivers": "List of Formula One World Drivers' Champions",
    "olympics": "Olympic Games",
    "olympic games": "Olympic Games",
    "olympic records": "List of Olympic records in athletics",
    "ufc": "Ultimate Fighting Championship",
    "mma": "Mixed martial arts",
    "offside rule": "Offside (association football)",
    "offside football": "Offside (association football)",
    "drs cricket": "Decision Review System",
    "cricket drs": "Decision Review System",
    "fastest centuries odi": "List of fastest centuries in One Day International cricket",
    "fastest odi centuries": "List of fastest centuries in One Day International cricket",
    "india olympics": "India at the Olympics",
    "kabaddi": "Kabaddi",
    "pro kabaddi": "Pro Kabaddi League",
    "hockey": "Field hockey",
    "badminton": "Badminton",
    "swimming records": "List of world records in swimming",
    "usain bolt": "Usain Bolt",
    "muhammad ali": "Muhammad Ali",
    "mike tyson": "Mike Tyson",
    "tiger woods": "Tiger Woods",
    "roger federer": "Roger Federer",
    "rafael nadal": "Rafael Nadal",
    "novak djokovic": "Novak Djokovic",
    "lewis hamilton": "Lewis Hamilton",
    "max verstappen": "Max Verstappen",
    "biggest upsets sports": "Upset (competition)",
}

SPORT_EMOJIS = {
    "cricket": "🏏", "football": "⚽", "basketball": "🏀",
    "tennis": "🎾", "f1": "🏎️", "olympics": "🥇",
    "boxing": "🥊", "hockey": "🏑", "baseball": "⚾",
    "kabaddi": "🤼", "badminton": "🏸", "swimming": "🏊",
    "golf": "⛳", "rugby": "🏉", "general": "🏆",
    "mma": "🥊", "ufc": "🥊",
}


def _extract_keywords(query: str) -> str:
    """Extract meaningful keywords from a natural language question."""
    words = query.lower().split()
    keywords = [w for w in words if w not in QUESTION_WORDS and len(w) > 1]
    return " ".join(keywords)


def _find_topic_match(query: str) -> Optional[str]:
    """Try to match query against known sports topics."""
    q = query.lower().strip()
    # Direct match
    if q in TOPIC_MAP:
        return TOPIC_MAP[q]
    # Partial match — check if any topic key is in the query
    for key, title in TOPIC_MAP.items():
        if key in q:
            return title
    # Check if query words match any key
    keywords = _extract_keywords(q)
    for key, title in TOPIC_MAP.items():
        if key in keywords:
            return title
    return None


def search_wikipedia(query: str, num_results: int = 5) -> List[Dict]:
    """Search Wikipedia and return matching pages."""
    params = {
        "action": "query", "list": "search", "srsearch": query,
        "srnamespace": 0, "srlimit": num_results, "format": "json",
    }
    try:
        resp = requests.get(WIKI_API, params=params, timeout=10)
        data = resp.json()
        return [{
            "title": item["title"],
            "snippet": re.sub(r"<[^>]+>", "", item.get("snippet", "")),
            "pageid": item["pageid"],
        } for item in data.get("query", {}).get("search", [])]
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return []


def get_page_summary(title: str) -> Optional[Dict]:
    """Get page summary from Wikipedia REST API."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "SportsGPT/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            return {
                "title": data.get("title", title),
                "extract": data.get("extract", ""),
                "description": data.get("description", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }
    except Exception as e:
        print(f"Wikipedia page error: {e}")
    return None


def get_page_content(title: str, max_chars: int = 3500) -> str:
    """Get detailed page content."""
    params = {
        "action": "query", "titles": title, "prop": "extracts",
        "exintro": False, "explaintext": True, "format": "json",
    }
    try:
        resp = requests.get(WIKI_API, params=params, timeout=10)
        pages = resp.json().get("query", {}).get("pages", {})
        for pid, page in pages.items():
            extract = page.get("extract", "")
            if extract:
                return extract[:max_chars]
    except Exception as e:
        print(f"Wikipedia content error: {e}")
    return ""


def format_sports_response(query: str) -> str:
    """Main function: Search Wikipedia for sports info and build response."""

    # Strategy 1: Try direct topic match
    topic_title = _find_topic_match(query)
    if topic_title:
        summary = get_page_summary(topic_title)
        if summary and summary["extract"]:
            return _build_response(summary, query, topic_title)

    # Strategy 2: Search with extracted keywords
    keywords = _extract_keywords(query)
    results = search_wikipedia(keywords)

    # Strategy 3: Search with original query
    if not results:
        results = search_wikipedia(query)

    # Strategy 4: Add "sport" context and search again
    if not results:
        results = search_wikipedia(f"{keywords} sport")

    if not results:
        return ("🔍 **No results found**\n\n"
                f"Couldn't find info about \"{query}\".\n\n"
                "**Try more specific queries like:**\n"
                "- \"Virat Kohli\"\n"
                "- \"FIFA World Cup 2022\"\n"
                "- \"NBA scoring leaders\"\n"
                "- \"IPL records\"")

    # Get info from best result
    top = results[0]
    summary = get_page_summary(top["title"])
    if not summary or not summary["extract"]:
        # Try next results
        for r in results[1:]:
            summary = get_page_summary(r["title"])
            if summary and summary["extract"]:
                top = r
                break

    if not summary or not summary["extract"]:
        return f"🔍 Found **{top['title']}** but couldn't load details. Try again!"

    return _build_response(summary, query, top["title"], results)


def _build_response(summary: Dict, query: str, title: str, related: List = None) -> str:
    """Build a nicely formatted response."""
    parts = []

    # Title & description
    parts.append(f"## {summary['title']}")
    if summary.get("description"):
        parts.append(f"*{summary['description']}*\n")

    # Main content
    parts.append(f"\n{summary['extract']}")

    # Extra detailed content
    detailed = get_page_content(title, max_chars=2000)
    if detailed and len(detailed) > len(summary["extract"]):
        extra = detailed[len(summary["extract"]):].strip()
        if extra and len(extra) > 100:
            sections = extra.split("\n\n")
            good_sections = [s.strip() for s in sections if 50 < len(s.strip()) < 500][:3]
            if good_sections:
                parts.append("\n---\n### 📋 More Details\n")
                for s in good_sections:
                    parts.append(f"{s}\n")

    # Related articles
    if related and len(related) > 1:
        parts.append("\n---\n### 🔗 Related\n")
        for r in related[1:4]:
            snippet = r["snippet"][:80] + "..." if len(r["snippet"]) > 80 else r["snippet"]
            parts.append(f"- **{r['title']}** — {snippet}")

    # Source
    if summary.get("url"):
        parts.append(f"\n\n📖 *Source: [Wikipedia]({summary['url']})*")

    return "\n".join(parts)
