import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from modules.crawler import crawl_info
from modules.llm_handler import run_llm, check_vllm_server, test_vllm_simple
from modules.stock_analyzer import analyze_stock_characteristics, summarize_crawling_process, explain_llm_processing_logic
from config import NUM_REFERENCES, CONFIG_LANGUAGES

# UI Components

def header_ui():
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">📈 AI 기반 포트폴리오 추천 리서치 도우미</h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">S&P500 종목 분석 및 AI 기반 투자 사유 분석</p>
    </div>
    """, unsafe_allow_html=True)


def sidebar_ui(default_start, default_end):
    st.sidebar.header("🔧 분석 설정")
    with st.sidebar.expander("📅 투자 기간 설정", expanded=True):
        start_date = st.date_input("투자 시작일:", value=default_start)
        end_date = st.date_input("투자 종료일:", value=default_end)
    with st.sidebar.expander("🎯 분석 조건", expanded=True):
        target_return = st.slider("목표 수익률 (%)", 0.0, 100.0, 10.0, 0.5)
        top_n = st.select_slider("추천 종목 수", list(range(1,21)), 5)
    # Language selection for LLM output
    language = st.sidebar.selectbox("언어 선택:", options=CONFIG_LANGUAGES, index=0)
    analyze = st.sidebar.button("🚀 분석 실행", type="primary")
    if analyze:
        st.session_state.analyze = True
    return start_date, end_date, target_return, top_n, language


def display_metrics(df):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("분석된 종목 수", len(df), delta="개")
    with col2:
        st.metric("평균 수익률", f"{df['Return (%)'].mean():.2f}%")
    with col3:
        st.metric("최고 수익률", f"{df['Return (%)'].max():.2f}%")
    with col4:
        st.metric("평균 리스크", f"{df['Risk (%)'].mean():.2f}%")


def display_table_and_chart(stock_data, start_date, end_date):
    df = pd.DataFrame(stock_data)
    display_df = df.copy()
    display_df['Return (%)'] = display_df['Return (%)'].round(2)
    display_df['Risk (%)'] = display_df['Risk (%)'].round(2)
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader("📊 종목별 수익률 & 리스크")
        st.dataframe(display_df, use_container_width=True)
    with col2:
        st.subheader("📈 포트폴리오 누적 수익률")
        chart_period = st.selectbox("차트 주기 선택", ["일봉","주봉","월봉"], index=0)
        with st.spinner('📈 포트폴리오 성과 계산 중...'):
            fig = go.Figure()
            for item in stock_data:
                data = yf.Ticker(item['Ticker']).history(start=str(start_date), end=str(end_date))
                if chart_period == "주봉":
                    data = data.resample('W').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
                elif chart_period == "월봉":
                    data = data.resample('M').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
                cumulative = (data['Close'].pct_change().add(1).cumprod() - 1) * 100  # % 단위로 변환
                fig.add_trace(go.Scatter(
                    x=cumulative.index, 
                    y=cumulative.values, 
                    mode='lines', 
                    name=item['Ticker'], 
                    line=dict(width=2),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                'Date: %{x}<br>' +
                                'Return: %{y:.2f}%<br>' +
                                '<extra></extra>'
                ))
            fig.update_layout(
                title=f"{chart_period} 누적 수익률 추이", 
                xaxis_title="날짜", 
                yaxis_title="누적 수익률 (%)", 
                hovermode='x unified', 
                height=600, 
                showlegend=True, 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_xaxes(rangeslider_visible=True)
            st.plotly_chart(fig, use_container_width=True)


def display_risk_info():
    with st.expander("📊 리스크(Risk) 계산 방법", expanded=False):
        st.markdown("""
        **리스크는 다음과 같이 계산됩니다:**
        1. **일별 수익률 계산**: 종가 기준 수익률 계산
        2. **표준편차 계산**: 일별 수익률들의 표준편차
        3. **백분율 변환**: 표준편차에 100 곱함
        **해석:**
        - 낮은 리스크 (<2%): 안정적
        - 중간 리스크 (2-5%): 보통
        - 높은 리스크 (>5%): 변동성 높음
        """, unsafe_allow_html=True)


def display_ai_analysis(stock_data, start_date, language):
    st.markdown("---")
    st.header("🤖 AI 투자 사유 분석")
    
    # vLLM 서버 상태 확인
    st.subheader("🔧 시스템 상태 확인")
    with st.spinner("vLLM 서버 연결 확인 중..."):
        vllm_status, vllm_message = check_vllm_server()
        
        if vllm_status:
            st.success(f"✅ {vllm_message}")
            
            # 간단한 테스트 수행
            test_status, test_message = test_vllm_simple()
            if test_status:
                st.success(f"✅ vLLM 테스트: {test_message}")
            else:
                st.warning(f"⚠️ vLLM 테스트 실패: {test_message}")
        else:
            st.error(f"❌ {vllm_message}")
            st.error("vLLM 서버를 시작해주세요. 터미널에서 다음 명령어를 실행하세요:")
            st.code("python -m vllm.entrypoints.openai.api_server --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 --port 8000")
            st.stop()
    
    # LLM 처리 로직 설명
    with st.expander("🧠 LLM 데이터 처리 로직", expanded=False):
        llm_logic = explain_llm_processing_logic()
        
        st.subheader("📥 입력 데이터 처리")
        for step in llm_logic["input_processing"]:
            st.write(f"• {step}")
        
        st.subheader("🔍 분석 방법론")
        for method in llm_logic["analysis_methodology"]:
            st.write(f"• {method}")
        
        st.subheader("📤 결과 생성")
        for output in llm_logic["output_generation"]:
            st.write(f"• {output}")
        
        st.subheader("✅ 품질 보증")
        for qa in llm_logic["quality_assurance"]:
            st.write(f"• {qa}")
    
    # 디버깅 정보 표시
    debug_container = st.container()
    
    progress = st.progress(0)
    status = st.empty()
    reasons = []
    
    for i, item in enumerate(stock_data):
        ticker = item['Ticker']
        status.text(f"🔍 {ticker} 분석 중 ({i+1}/{len(stock_data)})")
        progress.progress((i+1)/len(stock_data))
        
        with debug_container:
            st.info(f"🚀 {ticker} 크롤링 및 LLM 분석 시작...")
        
        try:
            # 크롤링 단계 디버깅
            with debug_container:
                st.write(f"📡 {ticker} 크롤링 중...")
            articles, links, debug = crawl_info(ticker, start_date)
            
            with debug_container:
                st.success(f"✅ {ticker} 크롤링 완료: {len(articles)}개 기사 수집")
                if len(articles) > 0:
                    st.write(f"첫 번째 기사 샘플: {articles[0][:100]}...")
                
            # LLM 분석 단계 디버깅
            with debug_container:
                st.write(f"🧠 {ticker} LLM 분석 중...")
            recommendation, review_content = run_llm(ticker, start_date, item['Return (%)'], articles, language)
            
            with debug_container:
                st.success(f"✅ {ticker} LLM 분석 완료")
                if recommendation:
                    st.write(f"LLM 응답 샘플: {recommendation[:100]}...")
                else:
                    st.warning(f"⚠️ {ticker} LLM 응답이 비어있습니다")
            
            # 크롤링 요약 및 주식 분석 추가
            crawling_summary = summarize_crawling_process(articles, debug)
            stock_analysis = analyze_stock_characteristics(
                ticker, 
                item['Return (%)'], 
                item['Risk (%)'], 
                start_date,
                '2024-12-31'
            )
        
        except Exception as e:
            with debug_container:
                st.error(f"❌ {ticker} 분석 중 오류 발생: {str(e)}")
                st.write(f"오류 세부사항: {type(e).__name__}")
            
            # 오류 시 기본값 설정
            articles, links, debug = [], [], [f"Error: {str(e)}"]
            recommendation = f"분석 오류 발생: {str(e)}"
            review_content = recommendation
            crawling_summary = {"data_quality": "오류", "total_sources": 0}
            stock_analysis = {"ticker": ticker, "investment_strategy": {"strategy": "분석 불가"}}
        
        # 분석 결과 저장
        
        reasons.append({
            **item, 
            '추천 사유': recommendation, 
            '크롤링 디버그': debug, 
            '참고 링크': links, 
            '크롤링된 기사': articles, 
            '리뷰 내용': review_content,
            '크롤링 요약': crawling_summary,
            '주식 분석': stock_analysis
        })
    progress.empty(); status.empty()
    st.subheader("📋 종목 추천 요약")
    for idx, r in enumerate(reasons):
        with st.expander(f"#{idx+1} {r['Ticker']} - 수익률: {r['Return (%)']:.2f}%", expanded= idx<3):
            c1, c2 = st.columns([1,3])
            with c1:
                st.metric("수익률", f"{r['Return (%)']:.2f}%")
                st.metric("리스크", f"{r['Risk (%)']:.2f}%")
            with c2:
                st.write("**AI 분석 결과:**")
                st.write(r['추천 사유'])
                
                # 딥러닝 모델 추천 섹션
                with st.expander("🧠 딥러닝 모델 추천", expanded=False):
                    analysis = r['주식 분석']
                    st.write(f"**추천 모델:** {analysis['primary_model']['model']}")
                    st.write(f"**선택 이유:** {analysis['primary_model']['reason']}")
                    st.write(f"**대안 모델:** {analysis['secondary_model']['model']}")
                    st.write(f"**대안 이유:** {analysis['secondary_model']['reason']}")
                    
                    st.write("**투자 전략 제안:**")
                    strategy = analysis['investment_strategy']
                    st.write(f"• **전략:** {strategy['strategy']}")
                    st.write(f"• **설명:** {strategy['description']}")
                    st.write(f"• **목표 기간:** {strategy['target_period']}")
                    st.write(f"• **리스크 관리:** {strategy['risk_management']}")
                
                # 크롤링 데이터 요약 섹션
                with st.expander("📊 크롤링 데이터 요약", expanded=False):
                    summary = r['크롤링 요약']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("총 소스", summary.get('total_sources', 0))
                        st.metric("성공한 크롤링", summary.get('successful_crawls', 0))
                        st.metric("Google Finance", summary.get('google_finance', 0))
                    with col2:
                        st.metric("Yahoo Finance", summary.get('yahoo_finance', 0))
                        st.metric("MarketWatch", summary.get('marketwatch', 0))
                        st.metric("RSS 피드", summary.get('rss_feeds', 0))
                    
                    st.write(f"**데이터 품질:** {summary.get('data_quality', '알 수 없음')}")
                    if summary.get('fallback_used'):
                        st.warning("⚠️ 폴백 콘텐츠가 사용되었습니다")
                    
                    if 'article_breakdown' in summary:
                        st.write("**기사 분석:**")
                        for source, count in summary['article_breakdown'].items():
                            st.write(f"• {source}: {count}개")
                    
                    st.write("**처리 과정:**")
                    for step in summary.get('processing_steps', []):
                        st.write(f"• {step}")
                
                with st.expander("🔍 크롤링 검증 정보", expanded=False):
                    st.write("**디버그:**")
                    for d in r['크롤링 디버그']:
                        st.text(d)
                    st.write("**크롤링된 기사 내용:**")
                    for idx, art in enumerate(r['크롤링된 기사'][:NUM_REFERENCES]): 
                        st.write(f"**기사 {idx+1}:** {art[:200]}...")
                if r['참고 링크']:
                    st.write("**참고 링크:**")
                    for idx, l in enumerate(r['참고 링크'][:NUM_REFERENCES]): 
                        if l and l.startswith('http'):
                            st.markdown(f"🔗 [참고자료 {idx+1}]({l})")
                # LLM이 리뷰한 내용 토글로 표시
                with st.expander("📝 LLM 리뷰 내용", expanded=False):
                    st.write(r['리뷰 내용'])
    
    # 크롤링 기능 테스트
    st.subheader("🔍 크롤링 기능 테스트")
    with st.expander("크롤링 테스트 실행", expanded=False):
        if st.button("크롤링 테스트 시작"):
            test_ticker = "AAPL"
            st.write(f"🧪 {test_ticker}로 크롤링 테스트 중...")
            
            try:
                test_articles, test_links, test_debug = crawl_info(test_ticker, start_date)
                
                st.success(f"✅ 크롤링 테스트 완료!")
                st.write(f"수집된 기사: {len(test_articles)}개")
                st.write(f"참고 링크: {len(test_links)}개")
                st.write(f"디버그 정보: {len(test_debug)}개")
                
                if test_articles:
                    st.write("첫 번째 기사 샘플:")
                    st.text(test_articles[0][:200])
                
                st.write("디버그 정보:")
                for debug_item in test_debug[:5]:
                    st.text(debug_item)
                    
            except Exception as e:
                st.error(f"❌ 크롤링 테스트 실패: {str(e)}")
                import traceback
                st.text(traceback.format_exc())

            # 분석 결과 상세 디버깅 정보 표시
            with debug_container:
                if recommendation and "Error" not in recommendation:
                    st.success(f"🎯 {ticker} 전체 분석 성공!")
                else:
                    st.error(f"🚨 {ticker} 분석에 문제가 있습니다")
                
                # 분석 통계
                st.write("📊 분석 통계:")
                st.write(f"   • 크롤링된 기사: {len(articles)}개")
                st.write(f"   • 참고 링크: {len(links)}개")
                st.write(f"   • LLM 응답 길이: {len(recommendation) if recommendation else 0}자")
                st.write(f"   • 데이터 품질: {crawling_summary.get('data_quality', '알 수 없음')}")
