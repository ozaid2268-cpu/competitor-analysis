"""
pages/3_Sentiment_Analysis.py
ML-based sentiment analysis of Google Play user reviews.
Uses DistilBERT via HuggingFace Transformers.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_reviews, compute_sentiments, sentiment_score

st.set_page_config(page_title="Sentiment Analysis", page_icon="💬", layout="wide")

st.title("💬 Sentiment Analysis")
st.markdown(
    "AI-powered analysis of user reviews using a pre-trained **DistilBERT** model from HuggingFace."
)
st.markdown("---")

# ── Guard ─────────────────────────────────────────────────────
if "search_results" not in st.session_state:
    st.warning("⚠️ No data found. Please go to the **Search** page and run a search first.")
    st.stop()

df = st.session_state["search_results"].copy()
query = st.session_state.get("search_query", "apps")

# ── Sidebar — select apps to analyze ─────────────────────────
with st.sidebar:
    st.header("⚙️ Analysis Settings")
    app_names = df["name"].tolist()
    selected_apps = st.multiselect(
        "Select apps to analyze",
        options=app_names,
        default=app_names[:5],  # default: first 5
        help="Fewer apps = faster analysis",
    )
    n_reviews = st.slider("Reviews per app", min_value=10, max_value=100, value=30, step=10)
    run_btn = st.button("🚀 Run Sentiment Analysis", use_container_width=True)

st.subheader(f"Analyzing reviews for: *{query}*")

if not selected_apps:
    st.info("👈 Select at least one app in the sidebar and click **Run Sentiment Analysis**.")
    st.stop()

# ── Run analysis ──────────────────────────────────────────────
if run_btn:
    selected_df = df[df["name"].isin(selected_apps)].reset_index(drop=True)
    scores_list = []

    progress = st.progress(0, text="Starting analysis...")

    for i, row in selected_df.iterrows():
        app_id   = row["app_id"]
        app_name = row["name"]

        progress.progress(
            (i + 1) / len(selected_df),
            text=f"Analyzing: {app_name[:40]}...",
        )

        with st.spinner(f"Fetching reviews for {app_name}..."):
            reviews = fetch_reviews(app_id, count=n_reviews)

        if not reviews:
            scores_list.append({
                "name": app_name, "app_id": app_id,
                "positive": 0, "negative": 0,
                "sentiment_score": 0.0, "total_reviews": 0,
            })
            continue

        with st.spinner(f"Computing sentiment for {app_name}..."):
            sent_df = compute_sentiments(reviews)

        score   = sentiment_score(sent_df)
        pos_pct = round((sent_df["label"] == "POSITIVE").mean() * 100, 1) if not sent_df.empty else 0
        neg_pct = round(100 - pos_pct, 1)

        scores_list.append({
            "name":            app_name,
            "app_id":          app_id,
            "positive":        pos_pct,
            "negative":        neg_pct,
            "sentiment_score": score,
            "total_reviews":   len(reviews),
        })

        # Store per-app review details in session state
        st.session_state[f"sent_{app_id}"] = sent_df

    progress.empty()
    st.session_state["sentiment_scores"] = pd.DataFrame(scores_list)
    st.success("✅ Sentiment analysis complete!")

# ── Display results ───────────────────────────────────────────
if "sentiment_scores" in st.session_state:
    scores_df = st.session_state["sentiment_scores"]

    # ── Overall sentiment score bar chart ─────────────────────
    st.markdown("#### 📊 Sentiment Score by App (0 = Very Negative → 1 = Very Positive)")
    fig = px.bar(
        scores_df.sort_values("sentiment_score", ascending=True),
        x="sentiment_score", y="name", orientation="h",
        color="sentiment_score",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        range_color=[0, 1],
        labels={"sentiment_score": "Score", "name": "App"},
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    # ── Stacked bar: positive vs negative ─────────────────────
    st.markdown("#### 🟢🔴 Positive vs Negative Review Breakdown")
    fig2 = px.bar(
        scores_df, x="name", y=["positive", "negative"],
        barmode="stack",
        color_discrete_map={"positive": "#22c55e", "negative": "#ef4444"},
        labels={"value": "Percentage (%)", "name": "App", "variable": "Sentiment"},
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-30)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Per-app review details ─────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔍 Review Details by App")
    selected_detail = st.selectbox("Select an app to see review details", scores_df["name"].tolist())
    detail_row = scores_df[scores_df["name"] == selected_detail].iloc[0]
    app_id_sel = detail_row["app_id"]

    d1, d2, d3 = st.columns(3)
    d1.metric("Sentiment Score", f"{detail_row['sentiment_score']:.2f}")
    d2.metric("✅ Positive",     f"{detail_row['positive']}%")
    d3.metric("❌ Negative",     f"{detail_row['negative']}%")

    sent_key = f"sent_{app_id_sel}"
    if sent_key in st.session_state:
        detail_df = st.session_state[sent_key]
        if not detail_df.empty:
            tab1, tab2 = st.tabs(["🟢 Positive Reviews", "🔴 Negative Reviews"])
            with tab1:
                pos_reviews = detail_df[detail_df["label"] == "POSITIVE"].head(10)
                for _, r in pos_reviews.iterrows():
                    st.success(f"⭐ {r['review'][:200]}")
            with tab2:
                neg_reviews = detail_df[detail_df["label"] == "NEGATIVE"].head(10)
                for _, r in neg_reviews.iterrows():
                    st.error(f"👎 {r['review'][:200]}")

    # ── Summary table ──────────────────────────────────────────
    with st.expander("📋 Full Sentiment Summary Table"):
        st.dataframe(scores_df, use_container_width=True)
else:
    st.info("👈 Select apps in the sidebar and click **Run Sentiment Analysis** to start.")
