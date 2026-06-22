"""
pages/1_Results_Table.py
Search Google Play and display results in an interactive table.
"""

import streamlit as st
import pandas as pd
from utils import fetch_apps

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Search Results", page_icon="🔎", layout="wide")

st.title("🔎 Search & Results")
st.markdown("Search the Google Play Store and explore the results below.")
st.markdown("---")

# ── Sidebar — search options ──────────────────────────────────
with st.sidebar:
    st.header("⚙️ Search Options")
    n_results = st.slider("Number of results", min_value=10, max_value=100, value=30, step=10)
    country   = st.selectbox("Country", ["us", "gb", "fr", "de", "ma"], index=0)
    lang      = st.selectbox("Language", ["en", "fr", "ar"], index=0)

# ── Search bar ────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Enter a search term",
        placeholder="e.g. mental health ai, note taking, fitness tracker...",
        label_visibility="collapsed",
    )
with col2:
    search_btn = st.button("🔍 Search", use_container_width=True)

# ── Run search ────────────────────────────────────────────────
if search_btn and query.strip():
    with st.spinner(f'Searching Google Play for "{query}"...'):
        df = fetch_apps(query.strip(), n_results=n_results, lang=lang, country=country)

    if df.empty:
        st.warning("No results found. Try a different search term.")
    else:
        # Persist results in session state so other pages can access them
        st.session_state["search_results"] = df
        st.session_state["search_query"]   = query.strip()
        st.success(f"✅ Found **{len(df)}** apps for *{query}*")

elif "search_results" not in st.session_state and not search_btn:
    st.info("👆 Enter a search term above and click **Search** to get started.")

# ── Display results ───────────────────────────────────────────
if "search_results" in st.session_state:
    df = st.session_state["search_results"]

    # ── Summary metrics ───────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📱 Total Apps",    len(df))
    m2.metric("⭐ Avg Rating",    f"{df['rating'].mean():.2f}")
    m3.metric("🆓 Free Apps",     int(df["free"].sum()))
    m4.metric("💰 Paid Apps",     int((~df["free"]).sum()))

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────
    with st.expander("🎛️ Filter Results", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
        with col_b:
            genres = ["All"] + sorted(df["genre"].dropna().unique().tolist())
            sel_genre = st.selectbox("Genre", genres)

    # Apply filters
    filtered = df[df["rating"] >= min_rating]
    if sel_genre != "All":
        filtered = filtered[filtered["genre"] == sel_genre]

    # ── Interactive table ─────────────────────────────────────
    st.subheader(f"📋 Results ({len(filtered)} apps)")
    st.dataframe(
        filtered[["name", "developer", "rating", "reviews", "installs", "price_type", "genre"]],
        use_container_width=True,
        column_config={
            "name":       st.column_config.TextColumn("App Name"),
            "developer":  st.column_config.TextColumn("Developer"),
            "rating":     st.column_config.NumberColumn("Rating ⭐", format="%.2f"),
            "reviews":    st.column_config.NumberColumn("Reviews 💬", format="%d"),
            "installs":   st.column_config.TextColumn("Installs 📥"),
            "price_type": st.column_config.TextColumn("Type"),
            "genre":      st.column_config.TextColumn("Genre"),
        },
        height=500,
    )

    # ── Download button ───────────────────────────────────────
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name=f"results_{st.session_state.get('search_query', 'apps')}.csv",
        mime="text/csv",
    )
