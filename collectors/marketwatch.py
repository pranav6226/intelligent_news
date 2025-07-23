import feedparser
from collectors.base import BaseNewsCollector
from typing import List, Dict, Any

class MarketWatchCollector(BaseNewsCollector):
    FEED_URL = "https://feeds.marketwatch.com/marketwatch/marketpulse/"

    def fetch(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        aliases = [alias.lower() for alias in company.get("aliases", [])]
        ticker = company.get("ticker", "").lower()
        
        try:
            feed = feedparser.parse(self.FEED_URL)
            all_entries = feed.entries
            articles = []
            
            for entry in all_entries:
                text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
                if any(alias in text for alias in aliases) or ticker in text:
                    articles.append({
                        "title": entry.get("title"),
                        "url": entry.get("link"),
                        "published": entry.get("published", entry.get("updated", "")),
                        "summary": entry.get("summary", ""),
                        "source": "MarketWatch"
                    })
            
            return articles
            
        except Exception as e:
            print(f"[WARNING] MarketWatch feed error: {e}")
            return [] 