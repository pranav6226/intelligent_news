from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.orchestrator import collect_all_news
from analytics.processor import analyze_articles
from db.supabase_client import get_articles, get_articles_by_company

app = Flask(__name__)
CORS(app)

# No longer need global variables since we're using Supabase directly

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/news')
def get_news():
    """API endpoint to get the latest news data from Supabase"""
    try:
        # Get articles from Supabase
        articles = get_articles(limit=100)
        print(f"[INFO] Retrieved {len(articles)} articles from Supabase")
        
        return jsonify({
            "articles": articles,
            "last_update": datetime.now().isoformat(),
            "total_articles": len(articles)
        })
    except Exception as e:
        print(f"[ERROR] Failed to get news from Supabase: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/refresh')
def refresh_news():
    """Force refresh the news data by collecting new articles"""
    try:
        print("[INFO] Force refreshing news data...")
        # Collect and analyze new articles (this will save to Supabase)
        new_articles = collect_all_news()
        print(f"[INFO] Collected and saved {len(new_articles)} new articles to Supabase")
        
        # Get updated articles from Supabase
        articles = get_articles(limit=100)
        
        return jsonify({
            "success": True,
            "articles": articles,
            "last_update": datetime.now().isoformat(),
            "total_articles": len(articles)
        })
    except Exception as e:
        print(f"[ERROR] Failed to refresh news: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get statistics about the news data from Supabase"""
    try:
        articles = get_articles(limit=100)
        
        if not articles:
            return jsonify({"error": "No data available"}), 404
        
        # Calculate statistics
        companies = {}
        sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
        sources = {}
        
        for article in articles:
            # Company stats
            company = article.get("company_ticker", "Unknown")
            companies[company] = companies.get(company, 0) + 1
            
            # Sentiment stats
            sentiment = article.get("sentiment", "Neutral")
            if "Positive" in sentiment:
                sentiments["Positive"] += 1
            elif "Negative" in sentiment:
                sentiments["Negative"] += 1
            else:
                sentiments["Neutral"] += 1
            
            # Source stats
            source = article.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return jsonify({
            "companies": companies,
            "sentiments": sentiments,
            "sources": sources,
            "total_articles": len(articles)
        })
    except Exception as e:
        print(f"[ERROR] Failed to get stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<company_ticker>')
def get_articles_by_company_api(company_ticker):
    """Get articles for a specific company"""
    try:
        articles = get_articles_by_company(company_ticker, limit=50)
        return jsonify({
            "articles": articles,
            "company_ticker": company_ticker,
            "total_articles": len(articles)
        })
    except Exception as e:
        print(f"[ERROR] Failed to get articles for {company_ticker}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 