import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px

# ---- CONFIG ----
SUPABASE_URL = "https://rplrriktxdoivomgljhh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJwbHJyaWt0eGRvaXZvbWdsamhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwNzYyNjksImV4cCI6MjA3NzY1MjI2OX0.PR-n8uZDCpFX9hWjOEdMv8i2yJ_ARVAil7FRimvHdVs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---- LOAD DATA ----
@st.cache_data(ttl=900)
def load_data():
    resp = supabase.table("articles").select("*").limit(1000).execute()
    df = pd.DataFrame(resp.data)
    df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
    return df

df = load_data()

st.title("🗞️ LivePulse News Analytics Dashboard")

st.markdown("""
**Source:** Automated news aggregation using Python, Supabase, and AI.
""")

# ---- METRICS ----
col1, col2, col3 = st.columns(3)
col1.metric("Total Articles", f"{len(df):,}")
col2.metric("News Sources", df['source'].nunique())
col3.metric("Topics", df['topic'].nunique())

# ---- SENTIMENT PIE ----
st.subheader("News Sentiment Distribution")
sentiment_counts = df['sentiment'].value_counts()
fig1 = px.pie(
    names=sentiment_counts.index,
    values=sentiment_counts.values,
    color=sentiment_counts.index,
    color_discrete_map={'Positive': 'mediumseagreen','Negative': 'crimson','Neutral': 'goldenrod'})
st.plotly_chart(fig1, use_container_width=True)

# ---- ARTICLES OVER TIME ----
st.subheader("Articles by Publish Date")
by_day = df.groupby(df['published_date'].dt.date).size()
fig2 = px.bar(by_day, labels={'value':'Articles','index':'Date'})
st.plotly_chart(fig2, use_container_width=True)

# ---- SOURCE DISTRIBUTION ----
st.subheader("Top News Sources")
top_sources = df['source'].value_counts().sort_values(ascending=True)
fig3 = px.bar(
    top_sources,
    orientation='h',
    labels={'value':'# Articles','index':'Source'},
    color=top_sources,
)
st.plotly_chart(fig3, use_container_width=True)

# ---- LATEST ARTICLES TABLE ----
st.subheader("Most Recent Headlines")
show_n = st.slider("Show latest N articles:", 5, 50, 10)
df_sorted = df.sort_values("published_date", ascending=False)
st.dataframe(
    df_sorted[["published_date", "source", "title", "topic", "sentiment"]].head(show_n),
    use_container_width=True
)

st.info("Data updates every 15 minutes. Try adding new articles and refreshing!")

