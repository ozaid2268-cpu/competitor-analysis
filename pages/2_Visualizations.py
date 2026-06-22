"""
pages/2_Visualizations.py
Data visualizations for competitor analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")

st.title("📊 Data Visualizations")
st.markdown("Visual insights from the search results. Run a search first on the **Search** page.")
st.markdown("---")

# ── Guard — need data from page 1 ────────────────────────────
if "search_results" not in st.session_state:
    st.warning("⚠️ No data found. Please go to the **Search** page and run a search first.")
    st.stop()

df = st.session_state["search_results"].copy()
query = st.session_state.get("search_query", "apps")

# ── Sidebar — filter by App ───────────────────────────────────
with st.sidebar:
    st.header("🎛️ Filter Apps")
    all_ids = df["app_id"].tolist()
    all_names = df["name"].tolist()
    options = ["All"] + all_names
    selected = st.multiselect("Filter by App Name", options=all_names, default=[])
    if selected:
        df = df[df["name"].isin(selected)]
    st.caption(f"Showing {len(df)} apps")

st.subheader(f"Analysis for: *{query}*  —  {len(df)} apps")

# ── Row 1: Rating distribution + Top apps by rating ──────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ⭐ Rating Distribution")
    fig = px.histogram(
        df, x="rating", nbins=20,
        color_discrete_sequence=["#2563eb"],
        labels={"rating": "Rating", "count": "Number of Apps"},
    )
    fig.update_layout(bargap=0.1, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 🏆 Top 10 Apps by Rating")
    top10 = df[df["rating"] > 0].nlargest(10, "rating")
    fig2 = px.bar(
        top10, x="rating", y="name", orientation="h",
        color="rating", color_continuous_scale="Blues",
        labels={"rating": "Rating", "name": "App"},
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"}, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Free vs Paid + Genre distribution ──────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🆓 Free vs Paid Apps")
    pie_data = df["price_type"].value_counts().reset_index()
    pie_data.columns = ["Type", "Count"]
    fig3 = px.pie(
        pie_data, names="Type", values="Count",
        color_discrete_sequence=["#2563eb", "#f59e0b"],
        hole=0.4,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### 🗂️ Genre Distribution")
    genre_data = df["genre"].value_counts().reset_index()
    genre_data.columns = ["Genre", "Count"]
    fig4 = px.bar(
        genre_data.head(10), x="Genre", y="Count",
        color="Count", color_continuous_scale="Blues",
    )
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-30)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Top apps by reviews + Rating vs Reviews scatter ────
col5, col6 = st.columns(2)

with col5:
    st.markdown("#### 💬 Top 10 Apps by Number of Reviews")
    top_reviews = df.nlargest(10, "reviews")
    fig5 = px.bar(
        top_reviews, x="reviews", y="name", orientation="h",
        color="reviews", color_continuous_scale="Teal",
        labels={"reviews": "Reviews", "name": "App"},
    )
    fig5.update_layout(yaxis={"categoryorder": "total ascending"}, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown("#### 🔵 Rating vs Number of Reviews")
    fig6 = px.scatter(
        df, x="reviews", y="rating",
        hover_name="name", size="reviews",
        color="genre",
        labels={"reviews": "Number of Reviews", "rating": "Rating"},
    )
    fig6.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig6, use_container_width=True)

# ── Word Cloud from descriptions ──────────────────────────────
st.markdown("---")
st.markdown("#### ☁️ Word Cloud — App Descriptions")

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    text = " ".join(df["description"].dropna().tolist())
    if text.strip():
        wc = WordCloud(
            width=1000, height=400,
            background_color="white",
            colormap="Blues",
            max_words=100,
        ).generate(text)
        fig_wc, ax = plt.subplots(figsize=(12, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)
    else:
        st.info("No description text available for word cloud.")
except ImportError:
    st.info("Install wordcloud to see this chart: `pip install wordcloud`")

# ── Raw data expander ─────────────────────────────────────────
with st.expander("📋 View Raw Data"):
    st.dataframe(df, use_container_width=True)
