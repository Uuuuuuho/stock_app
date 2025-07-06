import requests
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from config import NUM_REFERENCES

# Try to import feedparser, fallback if not available
try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    print("⚠️ feedparser not available, RSS feeds will be skipped")

def get_user_agents():
    """Return a list of different user agents to rotate through"""
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]

def safe_request(url, headers, timeout=5, retries=1):
    """Make a safe HTTP request with retries and minimal delays"""
    for attempt in range(retries):
        try:
            # Reduced delay for faster processing
            time.sleep(random.uniform(0.1, 0.5))
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                return response
        except Exception as e:
            if attempt == retries - 1:
                raise e
    return None

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def crawl_google_finance(ticker):
    """Crawl Google Finance for stock information"""
    articles, links, debug = [], [], []
    try:
        url = f"https://www.google.com/search?q={ticker}+stock+news+finance&tbm=nws"
        headers = {'User-Agent': random.choice(get_user_agents())}
        response = safe_request(url, headers)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for news results
            news_results = soup.find_all('div', class_='SoaBEf')
            if not news_results:
                news_results = soup.find_all('div', class_='xrnccd')
            
            debug.append(f"✅ Google Finance: {len(news_results)} results found")
            
            for result in news_results[:NUM_REFERENCES//2]:
                try:
                    title_elem = result.find('div', class_='MBeuO') or result.find('h3')
                    snippet_elem = result.find('div', class_='GI74Re') or result.find('span', class_='st')
                    link_elem = result.find('a', href=True)
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text().strip()
                        snippet = snippet_elem.get_text().strip()
                        link = link_elem['href'] if link_elem else ""
                        
                        articles.append(f"[NEWS] {title}: {snippet}")
                        links.append(link)
                        debug.append(f"✅ Added: {title[:50]}...")
                except Exception as e:
                    debug.append(f"❌ Error parsing result: {e}")
        else:
            debug.append("❌ Failed to fetch Google Finance")
    except Exception as e:
        debug.append(f"❌ Google Finance error: {e}")
    
    return articles, links, debug

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def crawl_yahoo_finance(ticker):
    """Crawl Yahoo Finance for stock information"""
    articles, links, debug = [], [], []
    try:
        # Try Yahoo Finance news section
        url = f"https://finance.yahoo.com/quote/{ticker}/news"
        headers = {'User-Agent': random.choice(get_user_agents())}
        response = safe_request(url, headers)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for news articles
            news_items = soup.find_all('h3', class_='Mb(5px)')
            if not news_items:
                news_items = soup.find_all('div', attrs={'data-module': 'Stream'})
            
            debug.append(f"✅ Yahoo Finance: {len(news_items)} results found")
            
            for item in news_items[:NUM_REFERENCES//3]:
                try:
                    title = item.get_text().strip()
                    if title and len(title) > 10:
                        articles.append(f"[YAHOO] {title}")
                        links.append(f"https://finance.yahoo.com/quote/{ticker}/news")
                        debug.append(f"✅ Added: {title[:50]}...")
                except Exception as e:
                    debug.append(f"❌ Error parsing Yahoo item: {e}")
        else:
            debug.append("❌ Failed to fetch Yahoo Finance")
    except Exception as e:
        debug.append(f"❌ Yahoo Finance error: {e}")
    
    return articles, links, debug

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def crawl_marketwatch(ticker):
    """Crawl MarketWatch for stock information"""
    articles, links, debug = [], [], []
    try:
        url = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
        headers = {'User-Agent': random.choice(get_user_agents())}
        response = safe_request(url, headers)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for news headlines
            headlines = soup.find_all('a', class_='link')
            if not headlines:
                headlines = soup.find_all('h3', class_='article__headline')
            
            debug.append(f"✅ MarketWatch: {len(headlines)} results found")
            
            for headline in headlines[:NUM_REFERENCES//4]:
                try:
                    title = headline.get_text().strip()
                    if title and len(title) > 10 and 'stock' in title.lower():
                        articles.append(f"[MARKETWATCH] {title}")
                        href = headline.get('href', '')
                        if href.startswith('/'):
                            href = f"https://www.marketwatch.com{href}"
                        links.append(href)
                        debug.append(f"✅ Added: {title[:50]}...")
                except Exception as e:
                    debug.append(f"❌ Error parsing MarketWatch item: {e}")
        else:
            debug.append("❌ Failed to fetch MarketWatch")
    except Exception as e:
        debug.append(f"❌ MarketWatch error: {e}")
    
    return articles, links, debug

def crawl_rss_feeds(ticker):
    """Crawl RSS feeds for financial news"""
    articles, links, debug = [], [], []
    
    if not HAS_FEEDPARSER:
        debug.append("❌ feedparser not available, skipping RSS feeds")
        debug.append("💡 Install with: pip install feedparser")
        return articles, links, debug
    
    # List of financial RSS feeds
    rss_feeds = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.nasdaq.com/feed/rssoutbound?category=Stocks",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    ]
    
    for feed_url in rss_feeds:
        try:
            debug.append(f"🔍 Checking RSS: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            relevant_entries = []
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                if ticker.upper() in title.upper() or ticker.upper() in summary.upper():
                    relevant_entries.append(entry)
            
            debug.append(f"✅ RSS {feed_url}: {len(relevant_entries)} relevant entries")
            
            for entry in relevant_entries[:3]:
                try:
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    link = entry.get('link', '')
                    
                    content = f"{title}: {summary[:200]}..." if summary else title
                    articles.append(f"[RSS] {content}")
                    links.append(link)
                    debug.append(f"✅ Added RSS: {title[:50]}...")
                except Exception as e:
                    debug.append(f"❌ Error parsing RSS entry: {e}")
                    
        except Exception as e:
            debug.append(f"❌ RSS {feed_url} error: {e}")
    
    return articles, links, debug

def crawl_alternative_search(ticker):
    """Alternative search using DuckDuckGo or other search engines"""
    articles, links, debug = [], [], []
    try:
        # Use DuckDuckGo as alternative
        url = f"https://duckduckgo.com/html/?q={ticker}+stock+news+analysis"
        headers = {'User-Agent': random.choice(get_user_agents())}
        response = safe_request(url, headers)
        
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            
            debug.append(f"✅ DuckDuckGo: {len(results)} results found")
            
            for result in results[:NUM_REFERENCES//3]:
                try:
                    title = result.get_text().strip()
                    href = result.get('href', '')
                    if title and len(title) > 10:
                        articles.append(f"[SEARCH] {title}")
                        links.append(href)
                        debug.append(f"✅ Added: {title[:50]}...")
                except Exception as e:
                    debug.append(f"❌ Error parsing DuckDuckGo result: {e}")
        else:
            debug.append("❌ Failed to fetch DuckDuckGo")
    except Exception as e:
        debug.append(f"❌ DuckDuckGo error: {e}")
    
    return articles, links, debug

def generate_fallback_content(ticker):
    """Generate fallback content when no articles are found"""
    articles = [
        f"[ANALYSIS] {ticker} is a publicly traded company that requires fundamental and technical analysis",
        f"[MARKET] {ticker} stock performance should be evaluated based on company financials and market trends",
        f"[INVESTMENT] Consider {ticker}'s sector performance, earnings reports, and competitive position",
        f"[RISK] Evaluate {ticker}'s volatility, market cap, and correlation with broader market indices",
        f"[STRATEGY] {ticker} investment decisions should consider portfolio diversification and risk tolerance"
    ]
    
    links = ["#fallback-analysis"] * len(articles)
    debug = ["🔄 Generated fallback analysis content due to limited crawled data"]
    
    return articles, links, debug

def extract_content_from_url(url, max_chars=1000):
    """Extract meaningful content from a given URL"""
    try:
        headers = {'User-Agent': random.choice(get_user_agents())}
        response = safe_request(url, headers, timeout=10)
        
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'article', 'main', '.content', '.article-body', 
                '.post-content', '.entry-content', 'p'
            ]
            
            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_text = ' '.join([elem.get_text().strip() for elem in elements[:3]])
                    break
            
            if not content_text:
                content_text = soup.get_text()
            
            # Clean and limit content
            content_text = ' '.join(content_text.split())  # Remove extra whitespace
            return content_text[:max_chars] + "..." if len(content_text) > max_chars else content_text
            
    except Exception as e:
        return f"Error extracting content: {str(e)}"
    
    return ""

def analyze_link_relevance(url, ticker):
    """Analyze how relevant a link is to the given ticker"""
    try:
        # Simple relevance scoring based on URL and domain
        relevance_score = 0
        url_lower = url.lower()
        ticker_lower = ticker.lower()
        
        # High relevance domains
        high_relevance_domains = [
            'finance.yahoo.com', 'marketwatch.com', 'bloomberg.com',
            'reuters.com', 'cnbc.com', 'fool.com', 'seekingalpha.com'
        ]
        
        for domain in high_relevance_domains:
            if domain in url_lower:
                relevance_score += 10
                break
        
        # Ticker mention in URL
        if ticker_lower in url_lower:
            relevance_score += 15
        
        # Financial keywords in URL
        financial_keywords = ['stock', 'earnings', 'revenue', 'analysis', 'news', 'investment']
        for keyword in financial_keywords:
            if keyword in url_lower:
                relevance_score += 2
        
        return relevance_score
    except:
        return 0

def crawl_info_parallel(ticker, date, enabled_sources=None):
    """Enhanced parallel crawl function for faster processing"""
    if enabled_sources is None:
        enabled_sources = ['google']  # Default to fastest source only
    
    all_articles, reference_links, debug_info = [], [], []
    
    debug_info.append(f"🚀 Starting parallel crawl for {ticker}")
    debug_info.append(f"📅 Target date: {date}")
    debug_info.append(f"� Enabled sources: {enabled_sources}")
    
    # Define all available sources
    available_sources = {
        "google": ("Google Finance", crawl_google_finance),
        "yahoo": ("Yahoo Finance", crawl_yahoo_finance),
        "marketwatch": ("MarketWatch", crawl_marketwatch),
        "rss": ("RSS Feeds", crawl_rss_feeds),
        "alternative": ("Alternative Search", crawl_alternative_search)
    }
    
    # Filter sources based on enabled list
    sources_to_run = [
        (name, func) for key, (name, func) in available_sources.items() 
        if key in enabled_sources
    ]
    
    if not sources_to_run:
        sources_to_run = [("Google Finance", crawl_google_finance)]  # Fallback
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=min(len(sources_to_run), 3)) as executor:
        # Submit all tasks
        future_to_source = {
            executor.submit(crawl_func, ticker): source_name 
            for source_name, crawl_func in sources_to_run
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                articles, links, debug = future.result(timeout=10)  # 10 second timeout per source
                
                debug_info.append(f"📊 {source_name} results: {len(articles)} articles, {len(links)} links")
                
                all_articles.extend(articles)
                reference_links.extend(links)
                debug_info.extend(debug)
                
            except Exception as e:
                error_msg = f"❌ {source_name} failed: {e}"
                debug_info.append(error_msg)
    
    debug_info.append(f"📈 Total articles before fallback: {len(all_articles)}")
    
    # If we don't have enough content, add fallback
    if len(all_articles) < 3:
        debug_info.append("⚠️ Limited content found, adding fallback analysis")
        fallback_articles, fallback_links, fallback_debug = generate_fallback_content(ticker)
        all_articles.extend(fallback_articles)
        reference_links.extend(fallback_links)
        debug_info.extend(fallback_debug)
    
    # Ensure we have at least some content
    if not all_articles:
        all_articles = [f"[FALLBACK] Analysis needed for {ticker} stock performance and market position"]
        reference_links = ["#no-data-available"]
        debug_info.append("🔄 Using minimal fallback content")
    
    # Limit to reasonable number
    all_articles = all_articles[:NUM_REFERENCES]
    reference_links = reference_links[:NUM_REFERENCES]
    
    final_msg = f"✅ Final results: {len(all_articles)} articles, {len(reference_links)} links"
    debug_info.append(final_msg)
    
    return all_articles, reference_links, debug_info
