from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from keybert import KeyBERT
import time

load_dotenv()

# Initialize LangChain Chat LLM (OpenAI)
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.0, model="gpt-4.1-mini")

# Initialize KeyBERT for topic extraction
kw_model = KeyBERT()

sentiment_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    Classify the sentiment of the following news article as Positive, Negative, or Neutral.\n
    Article: {text}\n
    Sentiment:
    """
)

summary_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    Summarize the following news article in 2-3 sentences:\n
    Article: {text}\n
    Summary:
    """
)

impact_prompt = PromptTemplate(
    input_variables=["text", "company"],
    template="""
    Given the following news article about {company}, assess the likely impact on the company's stock price or market value.\n
    Respond with one of: Positive, Negative, Neutral, and provide a brief explanation.\n
    Article: {text}\n
    Impact:
    """
)

def detect_trends(article: Dict[str, Any]) -> List[str]:
    text = article.get("title", "") + ". " + article.get("summary", "")
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5)
    return [kw for kw, _ in keywords]

def assess_company_impact(article: Dict[str, Any]) -> str:
    text = article.get("title", "") + ". " + article.get("summary", "")
    company = article.get("company_name", "")
    print(f"[DEBUG] Calling LLM for company impact: {company} | Title: {article.get('title', '')}")
    t0 = time.time()
    impact = llm.invoke(impact_prompt.format(text=text, company=company)).content.strip()
    print(f"[DEBUG] LLM company impact done in {time.time() - t0:.2f}s")
    return impact

def analyze_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    analyzed = []
    for idx, article in enumerate(articles, 1):
        text = article.get("title", "") + ". " + article.get("summary", "")
        print(f"[DEBUG] Analyzing article {idx}/{len(articles)}: {article.get('title', '')}")
        # Sentiment
        print("[DEBUG] Calling LLM for sentiment...")
        t0 = time.time()
        sentiment = llm.invoke(sentiment_prompt.format(text=text)).content.strip()
        print(f"[DEBUG] LLM sentiment done in {time.time() - t0:.2f}s")
        # Summary
        print("[DEBUG] Calling LLM for summary...")
        t1 = time.time()
        summary = llm.invoke(summary_prompt.format(text=text)).content.strip()
        print(f"[DEBUG] LLM summary done in {time.time() - t1:.2f}s")
        # Trend detection (KeyBERT)
        print("[DEBUG] Detecting trends with KeyBERT...")
        trends = detect_trends(article)
        print(f"[DEBUG] KeyBERT trends: {trends}")
        # Company impact (LLM)
        impact = assess_company_impact(article)
        article["sentiment"] = sentiment
        article["summary_short"] = summary
        article["trend"] = trends
        article["company_impact"] = impact
        analyzed.append(article)
    print(f"[DEBUG] Finished analyzing {len(analyzed)} articles.")
    return analyzed 