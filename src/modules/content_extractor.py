import requests
from bs4 import BeautifulSoup
import time
import random
from config import NUM_REFERENCES

def extract_content_from_url(url, max_chars=2000):
    """Extract meaningful content from a given URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
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
            result_text = content_text[:max_chars] + "..." if len(content_text) > max_chars else content_text
            return result_text, None
            
    except Exception as e:
        return f"Error extracting content: {str(e)}", None
    
    return "", None

def analyze_link_relevance(url, ticker):
    """Analyze how relevant a link is to the given ticker"""
    try:
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

def get_enhanced_content_for_ticker(ticker, links, max_links=5):
    """Get enhanced content from the most relevant links for a ticker"""
    enhanced_content = []
    debug_info = []
    
    if not links:
        debug_info.append(f"❌ No links available for {ticker}")
        return enhanced_content, debug_info
    
    # Score and sort links by relevance
    scored_links = []
    for link in links:
        if link and link.startswith('http'):
            score = analyze_link_relevance(link, ticker)
            scored_links.append((score, link))
    
    # Sort by relevance score (highest first)
    scored_links.sort(key=lambda x: x[0], reverse=True)
    
    debug_info.append(f"📊 Analyzing {len(scored_links)} links for {ticker}")
    
    # Extract content from top links
    for i, (score, link) in enumerate(scored_links[:max_links]):
        try:
            debug_info.append(f"🔗 Extracting content from link {i+1} (score: {score})")
            content, _ = extract_content_from_url(link)
            
            if content and len(content.strip()) > 50:
                enhanced_content.append({
                    'url': link,
                    'content': content,
                    'relevance_score': score
                })
                debug_info.append(f"✅ Successfully extracted {len(content)} characters")
            else:
                debug_info.append(f"⚠️ Limited content from {link}")
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 2))
        
        except Exception as e:
            debug_info.append(f"❌ Error extracting from {link}: {str(e)}")
    
    debug_info.append(f"✅ Enhanced content extraction complete: {len(enhanced_content)} sources")
    return enhanced_content, debug_info
