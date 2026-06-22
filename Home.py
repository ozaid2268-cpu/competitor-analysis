"""
Home.py — Competitor Analysis App
Entry point: streamlit run Home.py
"""

import streamlit as st

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Competitor Analysis",
    page_icon="📱",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────
st.title("📱 Competitor Analysis App")
st.markdown("---")

# ── Two-column layout ─────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.header("🔍 Overview")
    st.markdown(
        """
        This app provides a **rapid competitor analysis** of mobile applications
        available on the **Google Play Store**.

        Based on a user-defined search query, it retrieves app data and delivers
        actionable insights through data visualizations and machine learning-based
        sentiment analysis of user reviews.
        """
    )

    st.header("✨ Key Features")
    st.markdown(
        """
        - 🔎 **Search** for apps by keyword on Google Play  
        - 📊 **Browse results** in an interactive data table  
        - 📈 **Visualize** ratings, genres, installs, and more  
        - 💬 **Sentiment Analysis** of user reviews using AI  
        - 🎛️ **Filter** results by app ID in the sidebar  
        """
    )

with col2:
    st.header("🚀 How to Use")
    st.markdown(
        """
        1. Navigate to **Search** in the sidebar  
        2. Enter a search term (e.g. *mental health ai*)  
        3. Click **Search** to retrieve results  
        4. Go to **Visualizations** to explore the data  
        5. Go to **Sentiment Analysis** to see AI-based review scores  
        """
    )

    st.header("🛠️ Improvements & Roadmap")
    st.markdown(
        """
        - Add data from **ProductHunt** and **GitHub**  
        - Include **time-series** tracking of ratings  
        - Add **LLM-based** feature gap analysis  
        - Export results as **PDF reports**  
        - Support **multi-language** reviews  
        """
    )

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.info("👈 Use the **sidebar** to navigate between pages.", icon="💡")
st.caption("Data Applications Lab 2 — June 2026")
