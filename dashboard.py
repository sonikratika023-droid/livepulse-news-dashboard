import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="LivePulse v2.0 Enhanced",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase connection
@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_supabase()

# Custom CSS
st.markdown("""
<style>
    /* Gradient Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.85rem;
        color: #10b981;
        margin-top: 0.5rem;
    }
    
    /* Success Banner */
    .success-banner {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 4px solid #10b981;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #f8f9fa;
    }
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: #1e1e1e;
        }
        .main-header {
            background: linear-gradient(135deg, #4c51bf 0%, #5b21b6 100%);
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/news.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Go to",
        ["📊 Dashboard", "📁 Upload Data", "⚙️ Settings", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Dark Mode Toggle
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    
    # Auto-Refresh
    auto_refresh = st.checkbox("🔄 Auto-Refresh", value=False)
    if auto_refresh:
        st.info("Auto-refresh enabled (30s)")

# Load data function
@st.cache_data(ttl=30)
def load_data():
    try:
        response = supabase.table('news_articles').select('*').execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# PAGE: Dashboard
if page == "📊 Dashboard":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📰 LivePulse v2.0 Enhanced</h1>
        <p>Real-Time News Intelligence Dashboard with Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if not df.empty:
        # Success banner
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        <div class="success-banner">
            ✅ Data loaded successfully! Last updated: {last_updated}
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">📊</div>
                <div class="metric-value">{len(df)}</div>
                <div class="metric-label">Total Articles</div>
                <div class="metric-change">↑ {len(df)} new</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            positive_pct = (df['sentiment'].value_counts(normalize=True).get('positive', 0) * 100)
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">😊</div>
                <div class="metric-value">{positive_pct:.1f}%</div>
                <div class="metric-label">Positive Sentiment</div>
                <div class="metric-change">↑ {len(df[df['sentiment']=='positive'])} articles</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            sources = df['source'].nunique() if 'source' in df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">📰</div>
                <div class="metric-value">{sources}</div>
                <div class="metric-label">News Sources</div>
                <div class="metric-change">↑ Active</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            topics = df['topic'].nunique() if 'topic' in df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">🏷️</div>
                <div class="metric-value">{topics}</div>
                <div class="metric-label">Topics Identified</div>
                <div class="metric-change">↑ Categories</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎭 Sentiment Distribution")
            sentiment_counts = df['sentiment'].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_sequence=['#fbbf24', '#10b981', '#ef4444'],
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Top 10 News Sources")
            if 'source' in df.columns:
                source_counts = df['source'].value_counts().head(10)
                fig = px.bar(
                    x=source_counts.values,
                    y=source_counts.index,
                    orientation='h',
                    color=source_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400, showlegend=False, yaxis_title="", xaxis_title="Articles")
                st.plotly_chart(fig, use_container_width=True)
        
        # Articles Table
        st.subheader("📄 Recent Articles")
        display_cols = ['title', 'source', 'sentiment', 'topic', 'published_date']
        available_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[available_cols].head(20), use_container_width=True)
        
    else:
        st.warning("⚠️ No data available. Please check your database connection.")

# PAGE: Upload Data
elif page == "📁 Upload Data":
    st.title("📁 Upload Data")
    st.write("Upload your enhanced news CSV file")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded: {len(df_upload)} records")
        st.dataframe(df_upload.head(10))
        
        if st.button("💾 Save to Database"):
            try:
                data_dict = df_upload.to_dict('records')
                supabase.table('news_articles').insert(data_dict).execute()
                st.success("✅ Data saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving data: {e}")

# PAGE: Settings
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.subheader("🎨 Appearance")
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    
    st.subheader("🔄 Data Refresh")
    refresh_interval = st.slider("Auto-refresh interval (seconds)", 10, 300, 30)
    
    st.subheader("📊 Display Options")
    show_charts = st.checkbox("Show charts", value=True)
    show_table = st.checkbox("Show data table", value=True)
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved!")

# PAGE: About
elif page == "ℹ️ About":
    st.title("ℹ️ About LivePulse v2.0 Enhanced")
    
    st.markdown("""
    ### 📰 LivePulse News Analytics Dashboard
    
    **Version:** 2.0 Enhanced
    
    **Features:**
    - 🤖 Automated news aggregation from 15+ sources
    - 📊 Real-time sentiment analysis
    - 🏷️ AI-powered topic categorization
    - 📈 Interactive data visualizations
    - 🔄 Auto-refresh capabilities
    - 📁 CSV data upload
    
    **Technology Stack:**
    - **Frontend:** Streamlit
    - **Database:** Supabase
    - **Visualization:** Plotly
    - **AI:** TextBlob, Custom NLP
    
    **Data Sources:**
    BBC News, CNN, Reuters, Al Jazeera, The Guardian, and more...
    
    ---
    
    **Developer:** Sonikaratika
    **GitHub:** [livepulse-news-dashboard](https://github.com/sonikratika023-droid/livepulse-news-dashboard)
    """)
