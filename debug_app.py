#!/usr/bin/env python3
"""
Debug 스크립트 - vLLM과 크롤링 문제 해결을 위한 독립적인 테스트
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_vllm_connection():
    """vLLM 서버 연결 테스트"""
    print("🔧 vLLM 서버 연결 테스트")
    print("=" * 50)
    
    try:
        from modules.llm_handler import check_vllm_server, test_vllm_simple
        
        # 서버 상태 확인
        status, message = check_vllm_server()
        print(f"서버 상태: {'✅' if status else '❌'} {message}")
        
        if status:
            # 간단한 테스트
            test_status, test_message = test_vllm_simple()
            print(f"테스트 결과: {'✅' if test_status else '❌'} {test_message}")
        
        return status
    except Exception as e:
        print(f"❌ vLLM 테스트 실패: {e}")
        return False

def test_crawler():
    """크롤링 기능 테스트"""
    print("\n🕷️ 크롤링 기능 테스트")
    print("=" * 50)
    
    try:
        from modules.crawler import crawl_info
        
        # 테스트 종목으로 크롤링
        ticker = "AAPL"
        date = "2022-01-01"
        
        print(f"📈 {ticker} 크롤링 테스트 시작...")
        articles, links, debug = crawl_info(ticker, date)
        
        print(f"\n📊 결과:")
        print(f"   수집된 기사: {len(articles)}개")
        print(f"   참고 링크: {len(links)}개")
        print(f"   디버그 항목: {len(debug)}개")
        
        print(f"\n📰 기사 샘플 (처음 3개):")
        for i, article in enumerate(articles[:3], 1):
            print(f"   {i}. {article[:100]}...")
        
        print(f"\n🔍 디버그 정보 (마지막 5개):")
        for debug_item in debug[-5:]:
            print(f"   {debug_item}")
        
        return len(articles) > 0
    except Exception as e:
        print(f"❌ 크롤링 테스트 실패: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_full_integration():
    """전체 통합 테스트"""
    print("\n🧩 전체 통합 테스트")
    print("=" * 50)
    
    try:
        from modules.crawler import crawl_info
        from modules.llm_handler import run_llm
        
        ticker = "AAPL"
        date = "2022-01-01"
        return_pct = 25.5
        language = "한국어"
        
        print(f"🚀 {ticker} 전체 프로세스 테스트...")
        
        # 1. 크롤링
        print("1️⃣ 크롤링 단계...")
        articles, links, debug = crawl_info(ticker, date)
        print(f"   ✅ 크롤링 완료: {len(articles)}개 기사")
        
        # 2. LLM 분석
        print("2️⃣ LLM 분석 단계...")
        recommendation, prompt = run_llm(ticker, date, return_pct, articles, language)
        print(f"   ✅ LLM 분석 완료")
        print(f"   📝 추천 내용: {recommendation[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """메인 디버깅 함수"""
    print("🔍 AI 포트폴리오 분석기 - 디버깅 스크립트")
    print("=" * 60)
    
    # 1. vLLM 서버 테스트
    vllm_ok = test_vllm_connection()
    
    # 2. 크롤링 테스트
    crawler_ok = test_crawler()
    
    # 3. 전체 통합 테스트 (vLLM이 작동할 때만)
    if vllm_ok and crawler_ok:
        integration_ok = test_full_integration()
    else:
        integration_ok = False
        print("\n⚠️ vLLM 또는 크롤링 문제로 통합 테스트 건너뜀")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("🎯 테스트 결과 요약:")
    print(f"   vLLM 서버: {'✅ 정상' if vllm_ok else '❌ 문제'}")
    print(f"   크롤링: {'✅ 정상' if crawler_ok else '❌ 문제'}")
    print(f"   전체 통합: {'✅ 정상' if integration_ok else '❌ 문제'}")
    
    if not vllm_ok:
        print("\n💡 vLLM 서버 시작 방법:")
        print("   python -m vllm.entrypoints.openai.api_server --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 --port 8000")
    
    if not crawler_ok:
        print("\n💡 크롤링 문제 해결:")
        print("   pip install feedparser")
        print("   인터넷 연결 확인")
    
    print("\n🏁 디버깅 완료!")

if __name__ == "__main__":
    main()
