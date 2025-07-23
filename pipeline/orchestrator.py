from collectors.google_news import GoogleNewsCollector
from collectors.yahoo_finance import YahooFinanceCollector
from collectors.bloomberg import BloombergCollector
from collectors.financial_times import FinancialTimesCollector
from collectors.marketwatch import MarketWatchCollector
from companies.list import companies
from typing import List, Dict, Any
from analytics.processor import analyze_articles
from db.supabase_client import get_seen_urls, add_seen_urls, insert_articles
import time

collectors = [
    GoogleNewsCollector(),
    YahooFinanceCollector(),
    BloombergCollector(),
    FinancialTimesCollector(),
    MarketWatchCollector()
]

def deduplicate_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_urls = set()
    seen_titles = set()
    unique_articles = []
    for article in articles:
        url = article.get("url", "").strip()
        title = article.get("title", "").strip().lower()
        if url and url not in seen_urls:
            seen_urls.add(url)
            seen_titles.add(title)
            unique_articles.append(article)
        elif title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    return unique_articles

def filter_fresh_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    print("[DEBUG] Starting freshness filter...")
    t0 = time.time()
    try:
        seen_urls = get_seen_urls()
        print(f"[DEBUG] Retrieved {len(seen_urls)} seen URLs from Supabase in {time.time() - t0:.2f}s")
    except Exception as e:
        print(f"[ERROR] Failed to fetch seen URLs from Supabase: {e}")
        seen_urls = set()
    fresh_articles = [a for a in articles if a.get("url", "").strip() not in seen_urls]
    print(f"[DEBUG] {len(fresh_articles)} fresh articles out of {len(articles)} after freshness filter.")
    new_urls = set(a.get("url", "").strip() for a in fresh_articles if a.get("url"))
    try:
        add_seen_urls(new_urls)
        print(f"[DEBUG] Added {len(new_urls)} new URLs to Supabase.")
    except Exception as e:
        print(f"[ERROR] Failed to add new URLs to Supabase: {e}")
    return fresh_articles

def validate_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    REQUIRED_FIELDS = [
        "title",
        "url",
        "published",
        "summary",
        "source",
        "company_ticker",
        "company_name"
    ]
    valid = []
    for article in articles:
        if all(article.get(field) for field in REQUIRED_FIELDS):
            valid.append(article)
    print(f"[DEBUG] {len(valid)} articles passed validation out of {len(articles)}.")
    return valid

def collect_all_news() -> List[Dict[str, Any]]:
    all_articles = []
    for company in companies:
        print(f"\n[DEBUG] Fetching articles for {company['ticker']} ({company['name']})")
        # Gather articles from each collector separately
        per_collector_articles = []
        for collector in collectors:
            collector_name = collector.__class__.__name__
            try:
                articles = collector.fetch(company)
                print(f"[DEBUG] {collector_name} returned {len(articles)} articles for {company['ticker']}")
                for article in articles:
                    article["company_ticker"] = company["ticker"]
                    article["company_name"] = company["name"]
                per_collector_articles.append(articles)
            except Exception as e:
                print(f"[ERROR] {collector_name} failed for {company['ticker']} ({company['name']}): {e}")
        # Round-robin selection up to 10 articles
        selected = []
        idx = 0
        while len(selected) < 10:
            added = False
            for articles in per_collector_articles:
                if idx < len(articles):
                    selected.append(articles[idx])
                    if len(selected) == 10:
                        break
                    added = True
            if not added:
                break  # No more articles to add
            idx += 1
        print(f"[DEBUG] Limited {company['ticker']} to {len(selected)} articles (round-robin)")
        all_articles.extend(selected)
    deduped_articles = deduplicate_articles(all_articles)
    print(f"[DEBUG] {len(deduped_articles)} articles after deduplication.")
    fresh_articles = filter_fresh_articles(deduped_articles)
    valid_articles = validate_articles(fresh_articles)
    print(f"[DEBUG] {len(valid_articles)} valid articles for analysis.")
    analyzed_articles = analyze_articles(valid_articles)
    # Save analyzed articles to Supabase
    if analyzed_articles:
        try:
            print(f"[DEBUG] Saving {len(analyzed_articles)} articles to Supabase...")
            insert_articles(analyzed_articles)
            print(f"[DEBUG] Successfully saved articles to Supabase.")
        except Exception as e:
            print(f"[ERROR] Failed to save articles to Supabase: {e}")
    return analyzed_articles 