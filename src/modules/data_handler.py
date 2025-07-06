import pandas as pd
import yfinance as yf
from functools import lru_cache

@lru_cache()
def get_sp500_tickers():
    """Fetch S&P 500 tickers from Wikipedia."""
    tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = tables[0]
    return df['Symbol'].tolist()


def get_stock_data(start_date, end_date, target_return, top_n=5):
    """Retrieve and filter stock data based on target return and risk."""
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
                    'Ticker': ticker,
                    'Return (%)': return_pct,
                    'Risk (%)': risk
                })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    # 수익률 기준 내림차순, 상위 종목 선택
    stock_data = sorted(stock_data, key=lambda x: x['Return (%)'], reverse=True)[:top_n]
    return stock_data
