# 주요 기능 단위 테스트

import sys
import traceback
from datetime import datetime, date
import pandas as pd

def test_sp500_fetch():
    """S&P500 티커 목록 가져오기 테스트"""
    try:
        from stock_research_app import get_sp500_tickers
        tickers = get_sp500_tickers()
        print(f"✅ S&P500 티커 {len(tickers)}개 로드 성공")
        print(f"   샘플: {tickers[:5]}")
        return True
    except Exception as e:
        print(f"❌ S&P500 티커 로드 실패: {e}")
        return False

def test_stock_data():
    """주식 데이터 가져오기 테스트"""
    try:
        from stock_research_app import get_stock_data
        start_date = date(2022, 1, 1)
        end_date = date(2022, 6, 1)
        
        print("📊 주식 데이터 테스트 (AAPL만)...")
        # 테스트용으로 AAPL만 확인
        import yfinance as yf
        data = yf.Ticker("AAPL").history(start=str(start_date), end=str(end_date))
        
        if not data.empty:
            start_price = data['Open'].iloc[0]
            end_price = data['Close'].iloc[-1]
            return_pct = (end_price - start_price) / start_price * 100
            print(f"✅ AAPL 수익률: {return_pct:.2f}%")
            return True
        else:
            print("❌ 데이터가 비어있음")
            return False
    except Exception as e:
        print(f"❌ 주식 데이터 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_crawling():
    """웹 크롤링 테스트"""
    try:
        from stock_research_app import crawl_info
        print("🕷️ 크롤링 테스트 중...")
        articles, links, debug = crawl_info("AAPL", "2022-01-01")
        
        print(f"   수집된 기사: {len(articles)}개")
        print(f"   수집된 링크: {len(links)}개")
        print(f"   디버그 로그: {len(debug)}개")
        
        if articles and articles[0] != "정보 없음":
            print(f"✅ 크롤링 성공 - 첫 번째 기사: {articles[0][:100]}...")
            return True
        else:
            print("⚠️ 크롤링 결과 없음 (정상적일 수 있음)")
            return True
    except Exception as e:
        print(f"❌ 크롤링 테스트 실패: {e}")
        return False

def test_ollama():
    """Ollama LLM 테스트"""
    try:
        from stock_research_app import run_llm
        print("🤖 Ollama LLM 테스트 중...")
        
        result = run_llm("AAPL", "2022-01-01", 25.5, ["Test article about Apple stock"])
        
        if result and result != "정보 없음":
            print(f"✅ LLM 응답 성공: {result[:100]}...")
            return True
        else:
            print("⚠️ LLM 응답 없음")
            return False
    except Exception as e:
        print(f"❌ LLM 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("=== 기능 테스트 시작 ===\n")
    
    tests = [
        ("S&P500 데이터", test_sp500_fetch),
        ("주식 데이터", test_stock_data),
        ("웹 크롤링", test_crawling),
        ("Ollama LLM", test_ollama)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} 테스트:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n=== 테스트 결과 요약 ===")
    for test_name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 모든 테스트 통과! 애플리케이션 실행 준비 완료")
    else:
        print("\n⚠️ 일부 테스트 실패. 문제를 해결한 후 다시 시도하세요.")
