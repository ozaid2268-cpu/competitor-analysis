"""
utils.py — Shared utility functions for the Competitor Analysis App
Contains: data fetching (Google Play API) + sentiment analysis helpers
"""

import streamlit as st
import pandas as pd
import time

# ─────────────────────────────────────────────────────────────
# DATA FETCHING — Google Play Store
# ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def fetch_apps(search_term: str, n_results: int = 30, lang: str = "en", country: str = "us") -> pd.DataFrame:
    """
    Search Google Play Store for apps matching search_term.
    Returns a cleaned DataFrame with app metadata.
    """
    try:
        from google_play_scraper import search
    except ImportError:
        st.error("google-play-scraper is not installed. Run: pip install google-play-scraper")
        return pd.DataFrame()

    try:
        results = search(
            search_term,
            n_hits=n_results,
            lang=lang,
            country=country,
        )
    except Exception as e:
        st.error(f"Error fetching apps: {e}")
        return pd.DataFrame()

    rows = []
    for app in results:
        rows.append({
            "app_id":      app.get("appId", ""),
            "name":        app.get("title", ""),
            "developer":   app.get("developer", ""),
            "rating":      app.get("score", 0.0),
            "reviews":     app.get("reviews", 0),
            "installs":    app.get("installs", "0"),
            "price":       app.get("price", 0),
            "free":        app.get("free", True),
            "genre":       app.get("genre", ""),
            "description": app.get("description", ""),
            "icon":        app.get("icon", ""),
            "url":         app.get("url", ""),
        })

    df = pd.DataFrame(rows)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)
    df["price_type"] = df["free"].apply(lambda x: "Free" if x else "Paid")
    return df


@st.cache_data(show_spinner=False)
def fetch_reviews(app_id: str, count: int = 50, lang: str = "en", country: str = "us") -> list:
    """
    Fetch user reviews for a specific app from Google Play.
    Returns a list of review text strings.
    """
    try:
        from google_play_scraper import reviews as gp_reviews, Sort
    except ImportError:
        return []

    try:
        result, _ = gp_reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.MOST_RELEVANT,
            count=count,
        )
        return [r["content"] for r in result if r.get("content")]
    except Exception as e:
        st.warning(f"Could not fetch reviews for {app_id}: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# SENTIMENT ANALYSIS — HuggingFace
# ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_sentiment_model():
    """
    Load the sentiment analysis pipeline once and cache it.
    Uses DistilBERT fine-tuned on SST-2 (fast + accurate).
    """
    try:
        from transformers import pipeline
        return pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
    except Exception as e:
        st.error(f"Could not load sentiment model: {e}")
        return None


def compute_sentiments(reviews: list) -> pd.DataFrame:
    """
    Run sentiment analysis on a list of review strings.
    Returns a DataFrame with columns: review, label, score.
    """
    if not reviews:
        return pd.DataFrame(columns=["review", "label", "score"])

    model = load_sentiment_model()
    if model is None:
        return pd.DataFrame(columns=["review", "label", "score"])

    # Truncate reviews to 512 chars to avoid token limit issues
    cleaned = [r[:512] for r in reviews if isinstance(r, str) and len(r.strip()) > 0]

    try:
        results = model(cleaned, truncation=True, max_length=512, batch_size=8)
    except Exception as e:
        st.error(f"Sentiment analysis failed: {e}")
        return pd.DataFrame(columns=["review", "label", "score"])

    df = pd.DataFrame(results)          # columns: label, score
    df["review"] = cleaned
    df = df[["review", "label", "score"]]
    return df


def sentiment_score(df: pd.DataFrame) -> float:
    """
    Returns a sentiment score between 0.0 (all negative) and 1.0 (all positive).
    """
    if df.empty:
        return 0.0
    positive = (df["label"] == "POSITIVE").sum()
    return round(positive / len(df), 2)
