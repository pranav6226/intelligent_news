import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_articles(articles):
    # Insert articles into the 'articles' table
    data = []
    for article in articles:
        # Prepare the row for insertion
        row = {
            "title": article.get("title"),
            "url": article.get("url"),
            "published": article.get("published"),
            "summary": article.get("summary"),
            "source": article.get("source"),
            "company_ticker": article.get("company_ticker"),
            "company_name": article.get("company_name"),
            "sentiment": article.get("sentiment"),
            "summary_short": article.get("summary_short"),
            "trend": article.get("trend"),
            "company_impact": article.get("company_impact"),
        }
        data.append(row)
    if data:
        supabase.table("articles").insert(data).execute()

def get_seen_urls():
    res = supabase.table("seen_urls").select("url").execute()
    return set(row["url"] for row in res.data or [])

def add_seen_urls(urls):
    data = [{"url": url} for url in urls]
    if data:
        supabase.table("seen_urls").upsert(data).execute()

def get_articles(limit=100):
    """Retrieve articles from Supabase with optional limit"""
    try:
        res = supabase.table("articles").select("*").order("published", desc=True).limit(limit).execute()
        return res.data or []
    except Exception as e:
        print(f"[ERROR] Failed to retrieve articles from Supabase: {e}")
        return []

def get_articles_by_company(company_ticker, limit=50):
    """Retrieve articles for a specific company"""
    try:
        res = supabase.table("articles").select("*").eq("company_ticker", company_ticker).order("published", desc=True).limit(limit).execute()
        return res.data or []
    except Exception as e:
        print(f"[ERROR] Failed to retrieve articles for {company_ticker}: {e}")
        return [] 