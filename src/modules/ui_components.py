import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from modules.crawler import crawl_info_parallel
from modules.llm_handler import run_llm, run_llm_stock_analysis, run_llm_with_enhanced_content, check_vllm_server, test_vllm_simple
from modules.stock_analyzer import analyze_stock_characteristics, summarize_crawling_process, explain_llm_processing_logic
from modules.content_extractor import extract_content_from_url # 추가
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
    # vLLM 서버 연결 상태 확인 버튼
    if st.sidebar.button("🔧 vLLM 서버 상태 확인"):
        from modules.llm_handler import check_vllm_server
        status, message = check_vllm_server()
        if status:
            st.sidebar.success(f"✅ {message}")
        else:
            st.sidebar.error(f"❌ {message}")
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
        st.subheader("📈 포트폴리오 주가 차트")
        
        # Chart period selection
        chart_period = st.selectbox("차트 주기 선택", ["일봉","주봉","월봉"], index=0, key="chart_period")
        
        # Moving Average trend line options
        st.write("**이동평균선 설정:**")
        ma_cols = st.columns(4)
        show_ma = {}
        with ma_cols[0]:
            show_ma[5] = st.checkbox("MA5", value=True, key="ma5")
        with ma_cols[1]:
            show_ma[20] = st.checkbox("MA20", value=True, key="ma20")
        with ma_cols[2]:
            show_ma[60] = st.checkbox("MA60", value=False, key="ma60")
        with ma_cols[3]:
            show_ma[120] = st.checkbox("MA120", value=False, key="ma120")
        
        # Stock selection checkboxes
        st.write("**표시할 종목 선택:**")
        selected_stocks = []
        cols = st.columns(min(3, len(stock_data)))  # Create up to 3 columns
        
        for i, item in enumerate(stock_data):
            with cols[i % 3]:
                if st.checkbox(
                    item['Ticker'], 
                    value=True, 
                    key=f"stock_select_{item['Ticker']}"
                ):
                    selected_stocks.append(item)
        
        if not selected_stocks:
            st.warning("⚠️ 적어도 하나의 종목을 선택해주세요.")
            return
            
        # Color palette for better visual separation
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
        with st.spinner('📈 포트폴리오 성과 계산 중...'):
            fig = go.Figure()
            
            # Process each selected stock with unique colors
            for idx, item in enumerate(selected_stocks):
                base_color = colors[idx % len(colors)]
                data = yf.Ticker(item['Ticker']).history(start=str(start_date), end=str(end_date))
                
                # Check if data is available
                if data.empty:
                    st.warning(f"⚠️ {item['Ticker']} 데이터를 가져올 수 없습니다.")
                    continue
                
                # Resample data based on selected period
                if chart_period == "주봉":
                    # Use 'W-FRI' for weekly data ending on Friday
                    data = data.resample('W-FRI').agg({
                        'Open':'first',
                        'High':'max',
                        'Low':'min',
                        'Close':'last',
                        'Volume':'sum'
                    }).dropna()
                elif chart_period == "월봉":
                    # Use 'M' for monthly data ending on last day of month
                    data = data.resample('M').agg({
                        'Open':'first',
                        'High':'max',
                        'Low':'min',
                        'Close':'last',
                        'Volume':'sum'
                    }).dropna()
                
                # Check if resampled data is available
                if data.empty:
                    st.warning(f"⚠️ {item['Ticker']} {chart_period} 데이터가 충분하지 않습니다.")
                    continue
                
                # Use Candlestick chart with custom colors
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=f"{item['Ticker']} 캔들",
                    increasing_line_color=base_color,
                    decreasing_line_color=base_color,
                    increasing_fillcolor=base_color,
                    decreasing_fillcolor=base_color,
                    opacity=0.8
                ))
                
                # Add Moving Average trend lines with coordinated colors
                ma_config = {
                    5: {'color': f"rgba({int(base_color[1:3], 16)}, {int(base_color[3:5], 16)}, {int(base_color[5:7], 16)}, 0.9)", 'style': 'solid', 'width': 1.5},
                    20: {'color': f"rgba({int(base_color[1:3], 16)}, {int(base_color[3:5], 16)}, {int(base_color[5:7], 16)}, 0.7)", 'style': 'dash', 'width': 2},
                    60: {'color': f"rgba({int(base_color[1:3], 16)}, {int(base_color[3:5], 16)}, {int(base_color[5:7], 16)}, 0.5)", 'style': 'dot', 'width': 2.5},
                    120: {'color': f"rgba({int(base_color[1:3], 16)}, {int(base_color[3:5], 16)}, {int(base_color[5:7], 16)}, 0.3)", 'style': 'dashdot', 'width': 3}
                }
                
                ma_names = {5: 'MA5', 20: 'MA20', 60: 'MA60', 120: 'MA120'}
                
                for period in [5, 20, 60, 120]:
                    if show_ma.get(period, False) and len(data) >= period:
                        ma_values = data['Close'].rolling(window=period).mean()
                        config = ma_config[period]
                        
                        fig.add_trace(go.Scatter(
                            x=data.index,
                            y=ma_values,
                            mode='lines',
                            name=f'{item["Ticker"]} {ma_names[period]}',
                            line=dict(
                                color=config['color'], 
                                width=config['width'], 
                                dash=config['style']
                            ),
                            opacity=0.8,
                            hovertemplate=f'<b>{item["Ticker"]} {ma_names[period]}</b><br>' +
                                        'Date: %{x}<br>' +
                                        f'{ma_names[period]}: $%{{y:.2f}}<br>' +
                                        '<extra></extra>'
                        ))
            fig.update_layout(
                title=f"{chart_period} 주가 차트 ({len(selected_stocks)}개 종목)", 
                xaxis_title="날짜", 
                yaxis_title="주가 ($)", 
                hovermode='x unified', 
                height=800,  # Increased height for better visibility
                showlegend=True, 
                legend=dict(
                    orientation="v", 
                    yanchor="top", 
                    y=1, 
                    xanchor="left", 
                    x=1.01,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1
                ),
                margin=dict(r=200),  # Add right margin for legend
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.05),
                    rangeselector=dict(
                        buttons=list([
                            dict(count=7, label="7D", step="day", stepmode="backward"),
                            dict(count=30, label="1M", step="day", stepmode="backward"),
                            dict(count=90, label="3M", step="day", stepmode="backward"),
                            dict(count=180, label="6M", step="day", stepmode="backward"),
                            dict(label="전체", step="all")
                        ])
                    )
                ),
                dragmode='zoom',  # Enable zoom functionality
                plot_bgcolor='rgba(240,240,240,0.3)',  # Light background
                paper_bgcolor='white'
            )
            
            # Add custom controls description
            st.info("💡 **차트 조작법:** 드래그로 확대, 더블클릭으로 전체보기, 범위선택 버튼 활용")
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
    
    # vLLM 서버 상태 확인 - 토글로 변경
    with st.expander("🔧 시스템 상태 확인", expanded=False):
        with st.spinner("vLLM 서버 연결 확인 중..." if language == "한국어" else "Checking vLLM server connection..."):
            vllm_status, vllm_message = check_vllm_server()
            
            if vllm_status:
                success_msg = f"✅ {vllm_message}" if language == "한국어" else f"✅ vLLM Server Connected: {vllm_message}"
                st.success(success_msg)
                
                # 간단한 테스트 수행
                test_status, test_message = test_vllm_simple()
                if test_status:
                    test_success_msg = f"✅ vLLM 테스트: {test_message}" if language == "한국어" else f"✅ vLLM Test: {test_message}"
                    st.success(test_success_msg)
                else:
                    test_fail_msg = f"⚠️ vLLM 테스트 실패: {test_message}" if language == "한국어" else f"⚠️ vLLM Test Failed: {test_message}"
                    st.warning(test_fail_msg)
            else:
                error_msg = f"❌ {vllm_message}" if language == "한국어" else f"❌ vLLM Server Error: {vllm_message}"
                st.error(error_msg)
                
                if language == "한국어":
                    st.error("vLLM 서버를 시작해주세요. 터미널에서 다음 명령어를 실행하세요:")
                    st.code("python -m vllm.entrypoints.openai.api_server --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 --port 8000")
                    st.info("💡 WSL 환경에서는 scripts/wsl/start_vllm.sh 스크립트를 사용할 수 있습니다.")
                else:
                    st.error("Please start the vLLM server. Run the following command in terminal:")
                    st.code("python -m vllm.entrypoints.openai.api_server --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 --port 8000")
                    st.info("💡 For WSL environment, you can use the scripts/wsl/start_vllm.sh script.")
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
    with st.expander("📈 실시간 분석 로그", expanded=False):
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
            articles, links, debug = crawl_info_parallel(ticker, start_date)
            
            with debug_container:
                st.success(f"✅ {ticker} 크롤링 완료: {len(articles)}개 기사 수집")
                if len(articles) > 0:
                    st.write(f"첫 번째 기사 샘플: {articles[0][:100]}...")
                
            # LLM 분석 단계 디버깅 (Enhanced with link content)
            with debug_container:
                st.write(f"🧠 {ticker} 강화된 LLM 분석 중...")
            
            # Use enhanced LLM analysis with link content extraction
            recommendation, review_content, extraction_debug = run_llm_with_enhanced_content(
                ticker, start_date, item['Return (%)'], articles, links, language
            )
            
            with debug_container:
                st.success(f"✅ {ticker} 강화된 LLM 분석 완료")
                if recommendation:
                    st.write(f"LLM 응답 샘플: {recommendation[:100]}...")
                    if extraction_debug:
                        st.write(f"링크 추출 정보: {len(extraction_debug)}개 디버그 항목")
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
            extraction_debug = [f"Error during extraction: {str(e)}"]
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
            '주식 분석': stock_analysis,
            '링크 추출 디버그': extraction_debug if 'extraction_debug' in locals() else []
        })
    progress.empty(); status.empty()
    
    # 수집된 정보 요약 섹션 추가
    with st.expander("📋 수집된 정보 요약", expanded=True):
        generate_collected_info_summary(reasons, language, vllm_status)
    
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
                
                # 강화된 링크 분석 정보 표시
                if r.get('링크 추출 디버그'):
                    with st.expander("🔗 강화된 링크 분석", expanded=False):
                        st.write("**링크 콘텐츠 추출 과정:**")
                        for debug_item in r['링크 추출 디버그']:
                            st.text(debug_item)
                        
                        st.info("💡 상위 관련성 링크에서 추가 콘텐츠를 추출하여 더 상세한 투자 분석을 제공했습니다.")
    
def display_crawling_test_ui(start_date, language):
    """UI for crawling test tab."""
    st.subheader("🔍 크롤링 기능 테스트")
    
    # 종목 티커 기반 테스트
    st.write("**종목 티커 기반 크롤링 테스트:**")
    if st.button("AAPL 티커로 테스트"):
        st.session_state.run_ticker_test = True
        st.session_state.ticker_test_results = None

    if st.session_state.get('run_ticker_test'):
        with st.spinner("AAPL 크롤링 중..."):
            try:
                articles, links, debug = crawl_info_parallel("AAPL", start_date)
                st.session_state.ticker_test_results = {"success": True, "articles": articles, "links": links, "debug": debug}
            except Exception as e:
                import traceback
                st.session_state.ticker_test_results = {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        st.session_state.run_ticker_test = False
        st.rerun()

    if st.session_state.get('ticker_test_results'):
        res = st.session_state.ticker_test_results
        if res["success"]:
            st.success("✅ AAPL 크롤링 테스트 완료!")
            st.write(f"수집된 기사: {len(res['articles'])}개, 링크: {len(res['links'])}개")
            with st.expander("상세 결과 보기"):
                st.json(res)
        else:
            st.error(f"❌ AAPL 크롤링 테스트 실패: {res['error']}")

    st.markdown("---")
    
    # URL 기반 콘텐츠 요약 테스트
    st.write("**URL 기반 콘텐츠 요약 테스트:**")
    test_url = st.text_input("테스트할 기사 URL을 입력하세요:", key="test_url")
    
    if st.button("URL 콘텐츠 요약 실행"):
        st.session_state.run_url_summary_test = True
        st.session_state.url_summary_results = None

    if st.session_state.get('run_url_summary_test') and test_url:
        with st.spinner("URL 콘텐츠 추출 및 요약 중..."):
            try:
                # 1. 콘텐츠 추출
                content, _ = extract_content_from_url(test_url)
                
                # 2. LLM으로 요약
                if content:
                    if language == "한국어":
                        summary_prompt = f"다음 기사의 주요 내용을 상세히 한국어로 요약해주세요. 핵심 포인트, 수치, 중요한 정보를 모두 포함하여 충분히 설명해주세요:\n\n{content}"
                    else:
                        summary_prompt = f"Please provide a detailed summary of the following article in English. Include all key points, numbers, and important information with sufficient explanation:\n\n{content}"
                    
                    summary, _ = run_llm(summary_prompt, "", "URL 요약", language)
                    st.session_state.url_summary_results = {"success": True, "content": content, "summary": summary}
                else:
                    st.session_state.url_summary_results = {"success": False, "error": "콘텐츠를 추출할 수 없습니다."}

            except Exception as e:
                import traceback
                st.session_state.url_summary_results = {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        st.session_state.run_url_summary_test = False
        st.rerun()

    if st.session_state.get('url_summary_results'):
        res = st.session_state.url_summary_results
        if res["success"]:
            st.success("✅ URL 요약 테스트 완료!")
            st.write("**요약:**")
            st.write(res['summary'])
            with st.expander("추출된 원문 보기"):
                st.text(res['content'])
        else:
            st.error(f"❌ URL 요약 테스트 실패: {res['error']}")
            if "traceback" in res:
                st.text(res['traceback'])

def generate_collected_info_summary(reasons, language, vllm_status):
    """Generate a summary of collected information in the selected language."""
    
    if language == "한국어":
        st.subheader("📊 전체 데이터 수집 현황")
        
        if not vllm_status:
            st.error("⚠️ vLLM 서버 연결 문제로 AI 분석이 제한될 수 있습니다. 시스템 상태 확인을 통해 vLLM 서버를 시작해주세요.")
            st.info("💡 vLLM 서버 없이도 크롤링된 정보는 확인할 수 있지만, AI 기반 투자 분석은 제한됩니다.")
        
        # Overall statistics
        total_stocks = len(reasons)
        total_articles = sum(len(r.get('크롤링된 기사', [])) for r in reasons)
        total_links = sum(len(r.get('참고 링크', [])) for r in reasons)
        successful_analyses = sum(1 for r in reasons if r.get('추천 사유') and "Error" not in str(r.get('추천 사유', '')))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("분석 완료 종목", f"{successful_analyses}/{total_stocks}")
        with col2:
            st.metric("수집된 기사", total_articles)
        with col3:
            st.metric("참고 링크", total_links)
        with col4:
            success_rate = (successful_analyses / total_stocks * 100) if total_stocks > 0 else 0
            st.metric("성공률", f"{success_rate:.1f}%")
        
        # Data quality summary
        st.write("**📈 데이터 품질 분석:**")
        quality_counts = {}
        for r in reasons:
            quality = r.get('크롤링 요약', {}).get('data_quality', '알 수 없음')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        for quality, count in quality_counts.items():
            percentage = (count / total_stocks * 100) if total_stocks > 0 else 0
            st.write(f"• {quality}: {count}개 종목 ({percentage:.1f}%)")
        
        # Source-wise collection status
        st.write("**🔍 정보 소스별 수집 현황:**")
        source_summary = {
            'Google Finance': 0, 'Yahoo Finance': 0, 'MarketWatch': 0, 
            'RSS 피드': 0, 'DuckDuckGo': 0
        }
        
        for r in reasons:
            crawling_summary = r.get('크롤링 요약', {})
            for source in source_summary.keys():
                source_key = source.lower().replace(' ', '_')
                source_summary[source] += crawling_summary.get(source_key, 0)
        
        for source, count in source_summary.items():
            st.write(f"• {source}: {count}개 기사")
        
        # Enhanced analysis information
        enhanced_count = sum(1 for r in reasons if r.get('링크 추출 디버그'))
        if enhanced_count > 0:
            st.write("**🔗 강화된 링크 분석:**")
            st.write(f"• {enhanced_count}개 종목에서 추가 링크 콘텐츠 분석 완료")
            st.info("💡 상위 관련성 링크에서 추출한 추가 정보로 더 정확한 투자 분석을 제공합니다.")
        
        # Summary of issues if any
        error_count = sum(1 for r in reasons if "Error" in str(r.get('추천 사유', '')))
        if error_count > 0:
            st.warning(f"⚠️ {error_count}개 종목에서 분석 오류가 발생했습니다.")
            if not vllm_status:
                st.error("🔧 대부분의 오류는 vLLM 서버 연결 문제로 인한 것입니다. 시스템 상태를 확인해주세요.")
        
    else:  # English
        st.subheader("📊 Overall Data Collection Status")
        
        if not vllm_status:
            st.error("⚠️ vLLM server connection issues limit AI analysis capabilities. Please check system status to start the vLLM server.")
            st.info("💡 Crawled information is available without vLLM server, but AI-based investment analysis is limited.")
        
        # Overall statistics
        total_stocks = len(reasons)
        total_articles = sum(len(r.get('크롤링된 기사', [])) for r in reasons)
        total_links = sum(len(r.get('참고 링크', [])) for r in reasons)
        successful_analyses = sum(1 for r in reasons if r.get('추천 사유') and "Error" not in str(r.get('추천 사유', '')))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Analyzed Stocks", f"{successful_analyses}/{total_stocks}")
        with col2:
            st.metric("Articles Collected", total_articles)
        with col3:
            st.metric("Reference Links", total_links)
        with col4:
            success_rate = (successful_analyses / total_stocks * 100) if total_stocks > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Data quality summary
        st.write("**📈 Data Quality Analysis:**")
        quality_counts = {}
        for r in reasons:
            quality = r.get('크롤링 요약', {}).get('data_quality', 'Unknown')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        for quality, count in quality_counts.items():
            percentage = (count / total_stocks * 100) if total_stocks > 0 else 0
            st.write(f"• {quality}: {count} stocks ({percentage:.1f}%)")
        
        # Source-wise collection status
        st.write("**🔍 Information Source Collection Status:**")
        source_summary = {
            'Google Finance': 0, 'Yahoo Finance': 0, 'MarketWatch': 0, 
            'RSS Feeds': 0, 'DuckDuckGo': 0
        }
        
        for r in reasons:
            crawling_summary = r.get('크롤링 요약', {})
            source_mapping = {
                'Google Finance': 'google_finance',
                'Yahoo Finance': 'yahoo_finance', 
                'MarketWatch': 'marketwatch',
                'RSS Feeds': 'rss_feeds',
                'DuckDuckGo': 'duckduckgo'
            }
            for source, key in source_mapping.items():
                source_summary[source] += crawling_summary.get(key, 0)
        
        for source, count in source_summary.items():
            st.write(f"• {source}: {count} articles")
        
        # Enhanced analysis information
        enhanced_count = sum(1 for r in reasons if r.get('링크 추출 디버그'))
        if enhanced_count > 0:
            st.write("**🔗 Enhanced Link Analysis:**")
            st.write(f"• {enhanced_count} stocks completed additional link content analysis")
            st.info("💡 Provides more accurate investment analysis with additional information extracted from top relevance links.")
        
        # Summary of issues if any
        error_count = sum(1 for r in reasons if "Error" in str(r.get('추천 사유', '')))
        if error_count > 0:
            st.warning(f"⚠️ {error_count} stocks encountered analysis errors.")
            if not vllm_status:
                st.error("🔧 Most errors are due to vLLM server connection issues. Please check system status.")
