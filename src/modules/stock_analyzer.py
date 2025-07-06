from config import DL_MODEL_RECOMMENDATIONS

def analyze_stock_characteristics(ticker, return_pct, risk_pct, start_date, end_date):
    """Analyze stock characteristics and recommend appropriate DL model"""
    
    # Convert dates to pandas Timestamp for consistent calculation
    import pandas as pd
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Calculate investment period - use .total_seconds() for consistent calculation
    period_days = int((end_date - start_date).total_seconds() / (24 * 3600))
    
    # Determine stock characteristics
    if risk_pct > 5:
        volatility_category = "high_volatility"
    else:
        volatility_category = "low_volatility"
    
    if return_pct > 50:
        return_category = "high_return"
    else:
        return_category = "medium_return"
    
    # Primary recommendation based on volatility
    primary_recommendation = DL_MODEL_RECOMMENDATIONS[volatility_category]
    secondary_recommendation = DL_MODEL_RECOMMENDATIONS[return_category]
    
    # Generate analysis summary
    analysis = {
        "ticker": ticker,
        "period_days": period_days,
        "volatility_category": volatility_category,
        "return_category": return_category,
        "primary_model": primary_recommendation,
        "secondary_model": secondary_recommendation,
        "investment_strategy": generate_investment_strategy(return_pct, risk_pct, period_days)
    }
    
    return analysis

def generate_investment_strategy(return_pct, risk_pct, period_days):
    """Generate investment strategy based on stock performance"""
    
    if return_pct > 100 and risk_pct > 10:
        return {
            "strategy": "고수익 고위험 전략",
            "description": "단기 집중 투자, 손절매 라인 설정 필수",
            "target_period": "3-6개월",
            "risk_management": "포트폴리오의 5-10% 이하로 제한"
        }
    elif return_pct > 50 and risk_pct < 5:
        return {
            "strategy": "성장주 장기 투자",
            "description": "꾸준한 성장세, 장기 보유 권장",
            "target_period": "1-3년",
            "risk_management": "포트폴리오의 15-25% 배분 가능"
        }
    elif return_pct < 20 and risk_pct < 3:
        return {
            "strategy": "안전 자산 배분",
            "description": "포트폴리오 안정성 확보용",
            "target_period": "1년 이상",
            "risk_management": "포트폴리오의 30-40% 배분 가능"
        }
    else:
        return {
            "strategy": "균형 투자 전략",
            "description": "적당한 수익과 리스크의 균형",
            "target_period": "6개월-2년",
            "risk_management": "포트폴리오의 10-20% 배분"
        }

def summarize_crawling_process(articles, debug_info):
    """Summarize how crawling data was processed with enhanced source tracking"""
    
    summary = {
        "total_sources": 5,  # Google Finance, Yahoo Finance, MarketWatch, RSS, Alternative
        "successful_crawls": 0,
        "google_finance": 0,
        "yahoo_finance": 0,
        "marketwatch": 0,
        "rss_feeds": 0,
        "alternative_search": 0,
        "fallback_used": False,
        "processing_steps": [],
        "data_quality": "높음",
        "article_breakdown": {}
    }
    
    # Count articles by source type
    for article in articles:
        if "[NEWS]" in article:
            summary["google_finance"] += 1
        elif "[YAHOO]" in article:
            summary["yahoo_finance"] += 1
        elif "[MARKETWATCH]" in article:
            summary["marketwatch"] += 1
        elif "[RSS]" in article:
            summary["rss_feeds"] += 1
        elif "[SEARCH]" in article:
            summary["alternative_search"] += 1
        elif "[FALLBACK]" in article:
            summary["fallback_used"] = True
    
    # Count successful crawls from debug info
    for debug in debug_info:
        if "✅" in debug and ("results found" in debug or "Added" in debug):
            summary["successful_crawls"] += 1
    
    # Article breakdown for detailed view
    summary["article_breakdown"] = {
        "Google Finance 뉴스": summary["google_finance"],
        "Yahoo Finance": summary["yahoo_finance"], 
        "MarketWatch": summary["marketwatch"],
        "RSS 피드": summary["rss_feeds"],
        "대안 검색": summary["alternative_search"],
        "총 수집 기사": len(articles)
    }
    
    # Define enhanced processing steps
    summary["processing_steps"] = [
        "1. 다중 금융 데이터 소스 접근 (Google Finance, Yahoo, MarketWatch, RSS)",
        "2. 사용자 에이전트 로테이션으로 차단 방지",
        "3. HTML/XML 파싱 및 관련 콘텐츠 추출",
        "4. 소스별 컨텐츠 태깅 및 분류",
        "5. 중복 제거 및 관련성 기반 필터링",
        "6. 폴백 콘텐츠 생성 (필요시)",
        "7. 최종 데이터 검증 및 품질 평가"
    ]
    
    # Determine enhanced data quality
    total_real_articles = len(articles) - (1 if summary["fallback_used"] else 0)
    if total_real_articles >= 10 and summary["successful_crawls"] >= 8:
        summary["data_quality"] = "매우 높음"
    elif total_real_articles >= 6 and summary["successful_crawls"] >= 5:
        summary["data_quality"] = "높음"
    elif total_real_articles >= 3 and summary["successful_crawls"] >= 3:
        summary["data_quality"] = "보통"
    elif summary["fallback_used"]:
        summary["data_quality"] = "제한적 (폴백 사용)"
    else:
        summary["data_quality"] = "낮음"
    
    return summary

def explain_llm_processing_logic():
    """Explain enhanced LLM processing logic"""
    
    return {
        "input_processing": [
            "다중 소스 크롤링 데이터 통합 및 전처리",
            "소스별 태그를 포함한 구조화된 입력 생성",
            "종목 티커, 수익률, 투자 기간 컨텍스트 제공",
            "데이터 품질 지표 및 폴백 사용 여부 확인"
        ],
        "analysis_methodology": [
            "자연어 처리를 통한 다중 소스 감정 분석",
            "뉴스 소스별 신뢰도 가중치 적용",
            "시계열 뉴스 패턴과 주가 성과 상관관계 분석",
            "시장 동향, 기업 실적, 섹터 영향 종합 평가",
            "제한된 데이터 상황에서의 일반적 분석 제공"
        ],
        "output_generation": [
            "핵심 상승/하락 요인을 3-4줄로 상세 요약",
            "선택된 언어로 일관성 있는 전문적 분석 제공",
            "구체적 시장 동향 및 기업 실적 언급",
            "데이터 제한 시 적절한 면책 조항 포함"
        ],
        "quality_assurance": [
            "다중 소스 정보의 교차 검증 및 일관성 확인",
            "시간적 맥락 검토 (투자 시점 vs 뉴스 발생)",
            "논리적 인과관계 및 투자 합리성 평가",
            "언어별 출력 품질 및 전문성 보장",
            "폴백 콘텐츠 사용 시 투명한 고지"
        ]
    }
