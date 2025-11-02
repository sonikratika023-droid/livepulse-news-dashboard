"""
LivePulse Automated News Scraper (Simplified for Testing)
Scrapes 20+ news sources, saves to Supabase
AI sentiment will be added in cloud deployment
"""

import feedparser
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from supabase import create_client, Client
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# ========================================
# SUPABASE CONFIGURATION
# ========================================
SUPABASE_URL = "https://rplrriktxdoivomgljhh.supabase.co"  # Your Project URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJwbHJyaWt0eGRvaXZvbWdsamhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwNzYyNjksImV4cCI6MjA3NzY1MjI2OX0.PR-n8uZDCpFX9hWjOEdMv8i2yJ_ARVAil7FRimvHdVs"  # Your anon public key

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========================================
# NEWS SOURCES CONFIGURATION
# ========================================
news_sources = {
    # Indian News
    'Times of India': 'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',
    'The Hindu': 'https://www.thehindu.com/news/national/feeder/default.rss',
    'NDTV': 'https://feeds.feedburner.com/ndtvnews-top-stories',
    'India Today': 'https://www.indiatoday.in/rss/home',
    'Indian Express': 'https://indianexpress.com/feed/',
    'Hindustan Times': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
    'Zee News': 'https://zeenews.india.com/rss/india-national-news.xml',
    'DNA India': 'https://www.dnaindia.com/feeds/india.xml',
    'Business Standard': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
    'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
    'The Print': 'https://theprint.in/feed/',
    'News18': 'https://www.news18.com/rss/india.xml',
    'Scroll.in': 'https://scroll.in/feeds/articles.rss',
    'Firstpost': 'https://www.firstpost.com/rss/india.xml',
    'Live Mint': 'https://www.livemint.com/rss/news',
    
    # International News
    'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
    'CNN': 'http://rss.cnn.com/rss/cnn_topstories.rss',
    'Reuters': 'https://www.reutersagency.com/feed/',
    'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
    'The Guardian': 'https://www.theguardian.com/world/rss',
}

# ========================================
# SCRAPING FUNCTIONS
# ========================================
def scrape_news_feed(source_name, feed_url, max_articles=100, days_back=2):
    """Scrape news from RSS feed with date filtering"""
    articles = []
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    try:
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:max_articles]
        
        for entry in entries:
            try:
                pub_date_str = entry.get('published', entry.get('updated', ''))
                
                if pub_date_str:
                    try:
                        pub_date = date_parser.parse(pub_date_str)
                        pub_date = pub_date.replace(tzinfo=None)
                    except:
                        pub_date = None
                else:
                    pub_date = None
                
                if pub_date and pub_date >= cutoff_date:
                    # Simple sentiment based on keywords
                    title_desc = (entry.get('title', '') + ' ' + entry.get('summary', '')).lower()
                    
                    positive_words = ['success', 'win', 'growth', 'boost', 'gain', 'positive', 'improve', 'rise']
                    negative_words = ['crisis', 'fail', 'loss', 'decline', 'drop', 'negative', 'concern', 'threat']
                    
                    pos_count = sum(1 for word in positive_words if word in title_desc)
                    neg_count = sum(1 for word in negative_words if word in title_desc)
                    
                    if pos_count > neg_count:
                        sentiment, emoji, score = 'Positive', '😊', 0.7
                    elif neg_count > pos_count:
                        sentiment, emoji, score = 'Negative', '😟', 0.7
                    else:
                        sentiment, emoji, score = 'Neutral', '😐', 0.5
                    
                    article = {
                        'source': source_name,
                        'title': entry.get('title', 'No Title'),
                        'description': entry.get('summary', entry.get('description', '')),
                        'url': entry.get('link', ''),
                        'published_date': pub_date.strftime('%Y-%m-%d'),
                        'published_time': pub_date.strftime('%H:%M:%S'),
                        'sentiment': sentiment,
                        'sentiment_score': score,
                        'sentiment_emoji': emoji,
                        'topic': 'General News'
                    }
                    
                    if article['title'] != 'No Title' and article['url']:
                        articles.append(article)
                        
            except Exception as e:
                continue
                
    except Exception as e:
        print(f" Error scraping {source_name}: {str(e)}")
    
    return articles

def scrape_all_sources(days_back=2):
    """Scrape all sources in parallel"""
    print(" Starting news scraping...")
    print(f" Fetching news from last {days_back} days")
    print("="*60)
    
    all_articles = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for source_name, feed_url in news_sources.items():
            future = executor.submit(scrape_news_feed, source_name, feed_url, 100, days_back)
            futures.append((source_name, future))
        
        for source_name, future in futures:
            try:
                articles = future.result(timeout=30)
                all_articles.extend(articles)
                print(f" {source_name:25s} | {len(articles):3d} articles")
            except:
                print(f" {source_name:25s} | Failed")
    
    print("="*60)
    print(f" Total articles collected: {len(all_articles)}")
    return all_articles

# ========================================
# SAVE TO SUPABASE
# ========================================
def save_to_supabase(articles):
    """Save articles to Supabase database with detailed error logging"""
    print("\n💾 Saving to Supabase...")
    print(f"📊 Attempting to save {len(articles)} articles")
    
    saved_count = 0
    error_count = 0
    
    for idx, article in enumerate(articles):
        try:
            # Try to insert article
            result = supabase.table('articles').insert(article).execute()
            saved_count += 1
            
            # Show progress
            if (saved_count) % 50 == 0:
                print(f"✅ Saved {saved_count} articles so far...")
                
        except Exception as e:
            error_count += 1
            
            # Show first 5 errors in detail
            if error_count <= 5:
                print(f"\n❌ ERROR #{error_count}:")
                print(f"   Article: {article.get('title', 'Unknown')[:50]}...")
                print(f"   Error: {str(e)}")
                print(f"   Error Type: {type(e).__name__}")
            
            continue
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully saved: {saved_count} articles")
    print(f"❌ Failed to save: {error_count} articles")
    
    if error_count > 0:
        print(f"\n⚠️ IMPORTANT: Check errors above for details!")
        print(f"   Common issues:")
        print(f"   - Wrong API key")
        print(f"   - Table permissions (RLS enabled)")
        print(f"   - Column name mismatches")
    
    print(f"{'='*60}")
    return saved_count


# ========================================
# MAIN EXECUTION
# ========================================
def main():
    """Main scraper execution"""
    print("="*60)
    print(" LIVEPULSE AUTOMATED NEWS SCRAPER")
    print("="*60)
    print(f" Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Calculate days since Nov 1
    start_date = datetime(2025, 11, 1)
    days_since_nov1 = (datetime.now() - start_date).days + 1
    
    # Scrape news
    articles = scrape_all_sources(days_back=days_since_nov1)
    
    if not articles:
        print(" No articles collected!")
        return
    
    # Save to database
    saved = save_to_supabase(articles)
    
    # Summary
    print("\n" + "="*60)
    print(" SCRAPING COMPLETE!")
    print(f" Total articles processed: {len(articles)}")
    print(f" New articles saved: {saved}")
    print(f" Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()
