import feedparser
from collectors.base import BaseNewsCollector
from typing import List, Dict, Any

class YahooFinanceCollector(BaseNewsCollector):
    BASE_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

    def fetch(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        ticker = company.get("ticker")
        url = self.BASE_URL.format(ticker=ticker)
        
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries:
                articles.append({
                    "title": entry.get("title"),
                    "url": entry.get("link"),
                    "published": entry.get("published", entry.get("updated", "")),
                    "summary": entry.get("summary", ""),
                    "source": "Yahoo Finance"
                })
            return articles
            
        except Exception as e:
            print(f"[WARNING] Yahoo Finance feed error for {ticker}: {e}")
            return [] 