"""
LivePulse - Real-Time News Intelligence Dashboard
Author: Kratika Soni
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import os
from supabase import create_client

# Page Configuration
st.set_page_config(
    page_title="LivePulse",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main { padding: 2rem; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Admin password (ONLY YOU CAN UPLOAD)
ADMIN_PASSWORD = "kratika2025"  # Change this to your secret password

# Initialize Supabase
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
        key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
        if url and key:
            return create_client(url, key)
        return None
    except:
        return None

supabase = init_supabase()

@st.cache_data(ttl=300)
def load_data_from_supabase():
    if supabase:
        try:
            response = supabase.table('articles').select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                if 'published_date' in df.columns:
                    df['published_date'] = pd.to_datetime(df['published_date'])
                return df
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    return pd.DataFrame()

# Header
st.markdown("""
<div class="main-header">
    <h1>📰 LivePulse</h1>
    <p style='font-size: 1.2rem; margin-top: 0.5rem;'>
        Real-Time News Intelligence Dashboard with Advanced AI
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar - ADMIN ONLY UPLOAD
with st.sidebar:
    # Admin login section (hidden by default)
    with st.expander("🔐 Admin Access", expanded=False):
        admin_password = st.text_input("Enter Admin Password", type="password", key="admin_pwd")
        
        if admin_password == ADMIN_PASSWORD:
            st.success("✅ Admin access granted!")
            st.header("📁 Upload Data")
            uploaded_file = st.file_uploader(
                "Upload CSV (Admin only)",
                type=['csv'],
                help="Upload CSV file or use Supabase data"
            )
        elif admin_password:
            st.error("❌ Incorrect password!")
            uploaded_file = None
        else:
            uploaded_file = None
    
    st.markdown("---")
    
    # Settings (visible to all)
    st.header("⚙️ Settings")
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    
    st.markdown("---")
    
    # Refresh button (visible to all)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.header("📊 About")
    st.info("""
    **LivePulse**
    
    ✨ Features:
    - 20+ news sources
    - AI sentiment analysis
    - Topic clustering
    - Real-time updates
    - Advanced visualizations
    """)

# Load data
df = load_data_from_supabase()

# If admin uploaded file, use that instead
if 'uploaded_file' in locals() and uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

# Main Content
if not df.empty:
    st.success(f"✅ Data loaded successfully! Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📰 Total Articles", len(df), delta=f"{len(df)} new")
    with col2:
        pos_pct = (len(df[df['sentiment'] == 'Positive']) / len(df)) * 100
        st.metric("😊 Positive", f"{pos_pct:.1f}%")
    with col3:
        st.metric("📡 Sources", df['source'].nunique())
    with col4:
        st.metric("🏷️ Topics", df['topic'].nunique())
    
    st.markdown("---")
    
    # Visualizations
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("🎭 Sentiment Distribution")
        sentiment_counts = df['sentiment'].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            color=sentiment_counts.index,
            color_discrete_map={
                'Positive': '#10b981',
                'Negative': '#ef4444',
                'Neutral': '#6b7280'
            },
            hole=0.4
        )
        fig_sentiment.update_traces(textinfo='percent+label')
        fig_sentiment.update_layout(height=400)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col_right:
        st.subheader("📊 Top 10 Sources")
        source_counts = df['source'].value_counts().head(10)
        fig_sources = px.bar(
            x=source_counts.values,
            y=source_counts.index,
            orientation='h',
            color=source_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_sources.update_layout(
            xaxis_title="Articles",
            yaxis_title="Source",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_sources, use_container_width=True)
    
    st.markdown("---")
    
    # Topic Analysis
    st.subheader("🏷️ Topic Distribution")
    topic_counts = df['topic'].value_counts().head(10)
    fig_topics = px.bar(
        x=topic_counts.index,
        y=topic_counts.values,
        color=topic_counts.values,
        color_continuous_scale='Plasma'
    )
    fig_topics.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_topics, use_container_width=True)
    
    st.markdown("---")
    
    # Word Clouds
    st.subheader("☁️ Trending Keywords")
    col_wc1, col_wc2 = st.columns(2)
    
    with col_wc1:
        st.write("**Positive Keywords**")
        pos_text = ' '.join(df[df['sentiment'] == 'Positive']['title'].dropna())
        if pos_text:
            wc_pos = WordCloud(width=400, height=300, background_color='white', colormap='Greens').generate(pos_text)
            fig_wc, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wc_pos, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc)
    
    with col_wc2:
        st.write("**Negative Keywords**")
        neg_text = ' '.join(df[df['sentiment'] == 'Negative']['title'].dropna())
        if neg_text:
            wc_neg = WordCloud(width=400, height=300, background_color='white', colormap='Reds').generate(neg_text)
            fig_wc, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wc_neg, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc)
    
    st.markdown("---")
    
    # Search & Filter
    st.subheader("🔍 Search & Filter")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        search = st.text_input("🔎 Search", "")
    with col_s2:
        filter_sent = st.multiselect("Sentiment", df['sentiment'].unique(), default=df['sentiment'].unique())
    with col_s3:
        filter_src = st.multiselect("Source", sorted(df['source'].unique()), default=[])
    
    # Apply filters
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search, case=False, na=False) |
            filtered_df['description'].str.contains(search, case=False, na=False)
        ]
    if filter_sent:
        filtered_df = filtered_df[filtered_df['sentiment'].isin(filter_sent)]
    if filter_src:
        filtered_df = filtered_df[filtered_df['source'].isin(filter_src)]
    
    st.write(f"**Showing {len(filtered_df)} of {len(df)} articles**")
    
    # View Mode
    view_mode = st.radio("View:", ["📋 Table", "📄 Cards"], horizontal=True)
    
    if view_mode == "📋 Table":
        display_cols = ['source', 'published_date', 'title', 'sentiment', 'topic']
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        display_df = filtered_df[available_cols].head(50)
        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        # Article Cards
        for idx, row in filtered_df.head(50).iterrows():
            if row['sentiment'] == 'Positive':
                emoji, color = '😊', '#10b981'
            elif row['sentiment'] == 'Negative':
                emoji, color = '😟', '#ef4444'
            else:
                emoji, color = '😐', '#6b7280'
            
            with st.expander(f"{emoji} **{row['title']}**"):
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.markdown(f"**📰 Source:** {row['source']}")
                    st.markdown(f"**📅 Published:** {row.get('published_date', 'N/A')}")
                    st.markdown(f"**🏷️ Topic:** {row['topic']}")
                    st.markdown("**📝 Summary:**")
                    desc = row.get('description', 'No description.')
                    st.write(desc[:500] + '...' if len(desc) > 500 else desc)
                    if 'url' in row and row['url']:
                        st.markdown(f"**[🔗 Read Full Article]({row['url']})**")
                
                with col_b:
                    sentiment_score = row.get('sentiment_score', 0)
                    st.markdown(f"""
                    <div style='background: {color}; color: white; padding: 1rem;
                    border-radius: 10px; text-align: center;'>
                        <h3 style='margin: 0; color: white;'>{emoji}</h3>
                        <p style='margin: 0; color: white; font-weight: bold;'>{row['sentiment']}</p>
                        <p style='margin: 0; color: white; font-size: 0.9rem;'>
                            Score: {sentiment_score:.2f}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")

else:
    st.warning("⚠️ No data available.")
    st.info("💡 Data loads automatically from Supabase or run scraper.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p><strong>LivePulse</strong> | Built with Python & AI</p>
    <p> <b>Kratika Soni</b> |  sonikratika023@gmail.com</p>
</div>
""", unsafe_allow_html=True)
