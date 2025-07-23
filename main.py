from pipeline.orchestrator import collect_all_news
from db.supabase_client import insert_articles
from apscheduler.schedulers.blocking import BlockingScheduler
import json
import sys
import datetime

def run_pipeline():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{now}] Collecting and analyzing news articles...")
    print("[DEBUG] Calling collect_all_news()...")
    articles = collect_all_news()
    print(f"[DEBUG] collect_all_news() returned {len(articles)} articles.")
    # Limit to 50 articles for testing
    articles = articles[:50]
    print(f"[DEBUG] Processing {len(articles)} articles (limit applied).\n")
    print(f"\nTotal articles collected and analyzed: {len(articles)}\n")
    for i, article in enumerate(articles, 1):
        print(f"Article {i}:")
        print(json.dumps(article, indent=2, ensure_ascii=False))
        print("-" * 60)
    if articles:
        print("[DEBUG] Calling insert_articles()...")
        insert_articles(articles)
        print("[DEBUG] insert_articles() completed.")
        print("\nInserting articles into Supabase...")
        print("Done.")
    # Log to file
    with open("pipeline_run.log", "a") as f:
        f.write(f"\n[{now}] Run complete. Articles: {len(articles)}\n")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # Schedule to run every day at 7:00 AM
    scheduler.add_job(run_pipeline, 'cron', hour=7, minute=0)
    print("Scheduler started. Pipeline will run daily at 7:00 AM. Press Ctrl+C to exit.")
    try:
        run_pipeline()  # Run once immediately
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped.")
