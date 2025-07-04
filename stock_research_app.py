import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
from functools import lru_cache
import plotly.express as px
import plotly.graph_objects as go

# Fetch S&P500 tickers from Wikipedia
@lru_cache()
def get_sp500_tickers():
    tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = tables[0]
    return df['Symbol'].tolist()

def get_stock_data(start_date, end_date, target_return, top_n=5):
    sp500_tickers = get_sp500_tickers()
    stock_data = []
    for ticker in sp500_tickers:
        try:
            data = yf.Ticker(ticker).history(start=str(start_date), end=str(end_date))
            if data.empty:
                continue
            # 시작가와 종가
            start_price = data['Open'].iloc[0]
            end_price = data['Close'].iloc[-1]
            return_pct = (end_price - start_price) / start_price * 100
            # 리스크(변동성)
            daily_rets = data['Close'].pct_change().dropna()
            risk = daily_rets.std() * 100
            if return_pct >= target_return:
                stock_data.append({
                    "Ticker": ticker,
                    "Return (%)": return_pct,
                    "Risk (%)": risk
                })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    # 수익률 기준 내림차순, 상위 종목 선택
    stock_data = sorted(stock_data, key=lambda x: x['Return (%)'], reverse=True)[:top_n]
    return stock_data

def crawl_info(ticker, buy_date):
    search_engines = [
        f"https://www.google.com/search?q={ticker}+{buy_date}+stock+news",
        f"https://search.naver.com/search.naver?query={ticker}+{buy_date}+주식+뉴스",
        f"https://www.youtube.com/results?search_query={ticker}+{buy_date}+stock+analysis"
    ]
    
    all_articles = []
    reference_links = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in search_engines:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Google search results
            if 'google.com' in url:
                results = soup.find_all('div', class_='g')[:3]
                for res in results:
                    link_tag = res.find('a', href=True)
                    title_tag = res.find('h3')
                    snippet_tag = res.find('span', class_='aCOpRe')
                    if title_tag and snippet_tag and link_tag:
                        text = f"{title_tag.get_text()} - {snippet_tag.get_text()}"
                        all_articles.append(text)
                        reference_links.append(link_tag['href'])
            
            # Naver search results
            elif 'naver.com' in url:
                results = soup.find_all('div', class_='info_group')[:3]
                for res in results:
                    title_tag = res.find('a', class_='link_tit')
                    desc_tag = res.find('div', class_='dsc_wrap')
                    if title_tag and desc_tag:
                        text = f"{title_tag.get_text()} - {desc_tag.get_text()}"
                        all_articles.append(text)
                        reference_links.append(title_tag.get('href', 'https://search.naver.com'))
            
            # YouTube search results
            elif 'youtube.com' in url:
                results = soup.find_all('div', class_='ytd-video-renderer')[:2]
                for res in results:
                    title_tag = res.find('a', id='video-title')
                    if title_tag:
                        text = f"YouTube: {title_tag.get_text().strip()}"
                        all_articles.append(text)
                        video_link = title_tag.get('href', '')
                        if video_link.startswith('/watch'):
                            video_link = f"https://www.youtube.com{video_link}"
                        reference_links.append(video_link)
                        
        except Exception as e:
            print(f"Error crawling {url} for {ticker}: {e}")
            continue
    
    return (all_articles if all_articles else ["정보 없음"], 
            reference_links if reference_links else [])

def run_llm(ticker, buy_date, return_percentage, articles):
    prompt = f"""
    {buy_date}에 {ticker}에 투자했다면 오늘까지 수익률은 {return_percentage:.2f}%입니다.
    아래는 그 당시 주요 기사 내용입니다:
    {articles}
    이 종목이 상승한 이유를 3줄 이내로 정리해주세요.
    """
    try:
        result = subprocess.run(["ollama", "run", "llama3.1:8b"], input=prompt, text=True, capture_output=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running LLM for {ticker}: {e}")
        return "정보 없음"

def build_ui():
    # 페이지 설정
    st.set_page_config(
        page_title="AI 포트폴리오 분석기",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 헤더 섹션
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">📈 AI 기반 포트폴리오 추천 리서치 도우미</h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">S&P500 종목 분석 및 AI 기반 투자 사유 분석</p>
    </div>
    """, unsafe_allow_html=True)

    # 사이드바 입력 폼
    with st.sidebar:
        st.header("🔧 분석 설정")
        
        with st.expander("📅 투자 기간 설정", expanded=True):
            start_date = st.date_input("투자 시작일:", value=pd.to_datetime("2022-01-01"))
            end_date = st.date_input("투자 종료일:", value=pd.to_datetime("2022-06-01"))
        
        with st.expander("🎯 분석 조건", expanded=True):
            target_return = st.slider("목표 수익률 (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
            top_n = st.select_slider("추천 종목 수", options=list(range(1, 21)), value=5)
        
        st.markdown("---")
        analyze_button = st.button("🚀 분석 실행", type="primary", use_container_width=True)
        
        if analyze_button:
            st.session_state.analyze = True

    if analyze_button or st.session_state.get('analyze', False):
        with st.spinner('📊 S&P500 종목 데이터 분석 중...'):
            stock_data = get_stock_data(start_date, end_date, target_return, top_n)
        
        if stock_data:
            df = pd.DataFrame(stock_data)
            
            # 메트릭 카드
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("분석된 종목 수", len(df), delta="개")
            with col2:
                st.metric("평균 수익률", f"{df['Return (%)'].mean():.1f}%")
            with col3:
                st.metric("최고 수익률", f"{df['Return (%)'].max():.1f}%")
            with col4:
                st.metric("평균 리스크", f"{df['Risk (%)'].mean():.1f}%")
            
            st.markdown("---")
            
            # 테이블과 차트 섹션
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📊 종목별 수익률 & 리스크")
                # 테이블 데이터 포맷팅
                display_df = df.copy()
                display_df['Return (%)'] = display_df['Return (%)'].round(2)
                display_df['Risk (%)'] = display_df['Risk (%)'].round(2)
                st.dataframe(display_df, use_container_width=True)
            
            with col2:
                st.subheader("📈 포트폴리오 누적 수익률")
                with st.spinner('📈 포트폴리오 성과 계산 중...'):
                    # Plotly로 인터랙티브 차트 생성
                    fig = go.Figure()
                    
                    for item in stock_data:
                        data = yf.Ticker(item['Ticker']).history(start=str(start_date), end=str(end_date))
                        cumulative_return = data['Close'].pct_change().add(1).cumprod()
                        
                        fig.add_trace(go.Scatter(
                            x=cumulative_return.index,
                            y=cumulative_return.values,
                            mode='lines',
                            name=item['Ticker'],
                            line=dict(width=2),
                            hovertemplate='<b>%{fullData.name}</b><br>' +
                                        'Date: %{x}<br>' +
                                        'Cumulative Return: %{y:.3f}<br>' +
                                        '<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title="일별 누적 수익률 추이",
                        xaxis_title="날짜",
                        yaxis_title="누적 수익률",
                        hovermode='x unified',
                        height=600,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # 확대/축소 및 스크롤 가능하도록 설정
                    fig.update_xaxes(rangeslider_visible=True)
                    
                    st.plotly_chart(fig, use_container_width=True)

            # AI 분석 섹션
            st.markdown("---")
            st.header("🤖 AI 투자 사유 분석")
            
            # 진행상황 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            reasons = []
            for i, item in enumerate(stock_data):
                status_text.text(f"🔍 {item['Ticker']} 종목 분석 중... ({i+1}/{len(stock_data)})")
                progress_bar.progress((i + 1) / len(stock_data))
                
                articles, links = crawl_info(item['Ticker'], start_date)
                reason = run_llm(item['Ticker'], start_date, item['Return (%)'], articles)
                reasons.append({
                    "Ticker": item['Ticker'], 
                    "Return (%)": round(item['Return (%)'], 2), 
                    "Risk (%)": round(item['Risk (%)'], 2), 
                    "추천 사유": reason,
                    "참고 링크": links
                })
            
            # 완료 후 진행상황 숨기기
            progress_bar.empty()
            status_text.empty()
            
            # 결과 테이블을 더 보기 좋게 표시
            st.subheader("📋 종목 추천 요약")
            
            for i, reason in enumerate(reasons):
                with st.expander(f"#{i+1} {reason['Ticker']} - 수익률: {reason['Return (%)']}%", expanded=i<3):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric("수익률", f"{reason['Return (%)']}%")
                        st.metric("리스크", f"{reason['Risk (%)']}%")
                    with col2:
                        st.write("**AI 분석 결과:**")
                        st.write(reason['추천 사유'])
                        
                        if reason['참고 링크']:
                            st.write("**참고 링크:**")
                            for idx, link in enumerate(reason['참고 링크'][:3]):
                                if link and link.startswith('http'):
                                    st.markdown(f"🔗 [참고자료 {idx+1}]({link})")
        else:
            st.error("⚠️ 조건을 만족하는 종목이 없습니다. 목표 수익률을 낮춰보세요.")

if __name__ == "__main__":
    build_ui()
