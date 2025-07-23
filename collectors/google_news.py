import feedparser
from collectors.base import BaseNewsCollector
from typing import List, Dict, Any
from urllib.parse import quote_plus

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

class GoogleNewsCollector(BaseNewsCollector):
    BASE_URL = "https://news.google.com/rss/search?q={query}"

    def clean_summary(self, summary_html: str) -> str:
        if BeautifulSoup:
            soup = BeautifulSoup(summary_html, "html.parser")
            # Extract the text from the <a> tag (title)
            a_tag = soup.find("a")
            title = a_tag.get_text(strip=True) if a_tag else ""
            # Extract the text from the <font> tag (source)
            font_tag = soup.find("font")
            source = font_tag.get_text(strip=True) if font_tag else ""
            # Combine title and source if both exist
            if title and source:
                return f"{title} ({source})"
            elif title:
                return title
            else:
                # Fallback: get all text
                return soup.get_text(" ", strip=True)
        else:
            # Fallback: strip HTML tags manually
            import re
            text = re.sub('<[^<]+?>', '', summary_html)
            return text.replace("&nbsp;", " ").strip()

    def fetch(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Build query from aliases
        aliases = company.get("aliases", [])
        query = " OR ".join([f'\"{alias}\"' if ' ' in alias else alias for alias in aliases])
        url = self.BASE_URL.format(query=quote_plus(query))
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            summary_clean = self.clean_summary(entry.get("summary", ""))
            articles.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "published": entry.get("published", entry.get("updated", "")),
                "summary": summary_clean,
                "source": "Google News"
            })
        return articles 