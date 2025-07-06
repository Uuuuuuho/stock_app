#!/usr/bin/env python3
"""
Test script to verify enhanced crawler functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from modules.crawler import crawl_info

def test_enhanced_crawler():
    """Test the enhanced crawler with a sample ticker"""
    print("🧪 Testing Enhanced Crawler")
    print("=" * 50)
    
    # Test with a popular stock
    ticker = "AAPL"
    date = "2022-01-01"
    
    print(f"📈 Testing crawler for {ticker} since {date}")
    
    try:
        articles, links, debug = crawl_info(ticker, date)
        
        print(f"\n✅ Results:")
        print(f"   Articles collected: {len(articles)}")
        print(f"   Reference links: {len(links)}")
        print(f"   Debug entries: {len(debug)}")
        
        print(f"\n📰 Sample Articles (first 3):")
        for i, article in enumerate(articles[:3], 1):
            print(f"   {i}. {article[:100]}...")
        
        print(f"\n🔍 Debug Info (last 5):")
        for debug_item in debug[-5:]:
            print(f"   {debug_item}")
        
        print(f"\n🔗 Sample Links (first 3):")
        for i, link in enumerate(links[:3], 1):
            print(f"   {i}. {link}")
            
        print(f"\n✅ Enhanced crawler test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Crawler test failed: {e}")
        return False

if __name__ == "__main__":
    test_enhanced_crawler()
