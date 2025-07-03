import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import subprocess

def get_stock_data(buy_date, top_n):
    # Fetch S&P500 tickers
    sp500_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Example tickers
    stock_data = []

    for ticker in sp500_tickers:
        try:
            data = yf.Ticker(ticker).history(period="max")
            buy_price = data.loc[buy_date]['Close']
            today_price = data.iloc[-1]['Close']
            return_percentage = ((today_price - buy_price) / buy_price) * 100
            profit_on_1000 = ((today_price - buy_price) / buy_price) * 1000

            if return_percentage > 10:
                stock_data.append({
                    "Ticker": ticker,
                    "Buy Price": buy_price,
                    "Today Price": today_price,
                    "Return (%)": return_percentage,
                    "Profit on $1000": profit_on_1000
                })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    stock_data = sorted(stock_data, key=lambda x: x['Return (%)'], reverse=True)[:top_n]
    return stock_data

def crawl_info(ticker, buy_date):
    search_query = f"{ticker} {buy_date}"
    url = f"https://www.bing.com/search?q={search_query}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('li', class_='b_algo')[:3]
        articles = [result.text for result in results]
        return articles
    except Exception as e:
        print(f"Error crawling info for {ticker}: {e}")
        return ["정보 없음"]

def run_llm(ticker, buy_date, return_percentage, articles):
    prompt = f"""
    {buy_date}에 {ticker}에 투자했다면 오늘까지 수익률은 {return_percentage:.2f}%입니다.
    아래는 그 당시 뉴스들입니다: {articles}
    이 종목이 상승한 이유를 3줄 이내로 정리해주세요.
    """
    try:
        result = subprocess.run(["ollama", "run", "llama3"], input=prompt, text=True, capture_output=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running LLM for {ticker}: {e}")
        return "정보 없음"

def build_ui():
    st.title("AI 기반 종목 추천 리서치 도우미")

    buy_date = st.date_input("투자 날짜를 선택하세요:", value=pd.Timestamp("2022-01-01"))
    top_n = st.number_input("추천 종목 수를 입력하세요:", min_value=1, max_value=10, value=5)

    if st.button("분석 실행"):
        stock_data = get_stock_data(buy_date, top_n)

        if stock_data:
            st.subheader("수익률 상위 종목 바 차트")
            fig, ax = plt.subplots()
            tickers = [item['Ticker'] for item in stock_data]
            returns = [item['Return (%)'] for item in stock_data]
            ax.bar(tickers, returns, color='skyblue')
            ax.set_xlabel("Ticker")
            ax.set_ylabel("Return (%)")
            ax.set_title("Top Performing Stocks")
            st.pyplot(fig)

            st.subheader("종목 요약 테이블")
            st.table(pd.DataFrame(stock_data))

            st.subheader("종목 추천 이유 요약")
            reasons = []
            for item in stock_data:
                articles = crawl_info(item['Ticker'], buy_date)
                reason = run_llm(item['Ticker'], buy_date, item['Return (%)'], articles)
                reasons.append({"Ticker": item['Ticker'], "요약된 추천 사유": reason})

            st.table(pd.DataFrame(reasons))
        else:
            st.warning("10% 이상의 수익률을 가진 종목이 없습니다.")

if __name__ == "__main__":
    build_ui()
