import streamlit as st
import pandas as pd
from datetime import datetime

from modules.data_handler import get_stock_data
from modules.ui_components import (
    header_ui, sidebar_ui, display_metrics,
    display_table_and_chart, display_risk_info, display_ai_analysis,
    display_crawling_test_ui
)

# Main application

def build_app():
    # 초기 설정
    default_start = pd.to_datetime("2025-01-01").date()
    default_end = pd.to_datetime("2025-06-01").date()

    # 페이지 구성
    st.set_page_config(
        page_title="AI 포트폴리오 분석기",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    header_ui()
    # Sidebar returns start_date, end_date, target_return, top_n, language
    start_date, end_date, target_return, top_n, language = sidebar_ui(default_start, default_end)

    # 탭 생성
    tab1, tab2 = st.tabs(["🤖 AI 분석", "🔍 크롤링 테스트"])

    with tab1:
        if st.session_state.get('analyze', False):
            # 데이터 분석
            with st.spinner('📊 S&P500 종목 데이터 분석 중...'):
                stock_data = get_stock_data(start_date, end_date, target_return, top_n)

            if not stock_data:
                st.error("⚠️ 조건을 만족하는 종목이 없습니다. 목표 수익률를 낮춰보세요.")
                return

            # 메트릭 및 차트 표시
            display_metrics(pd.DataFrame(stock_data))
            st.markdown("---")
            display_table_and_chart(stock_data, start_date, end_date)
            display_risk_info()

            # AI 분석 (language 인자 추가)
            display_ai_analysis(stock_data, start_date, language)

            # 분석 상태 초기화
            st.session_state.analyze = False
        else:
            st.info("👈 사이드바에서 조건을 설정하고 '분석 시작' 버튼을 클릭하세요.")


    with tab2:
        display_crawling_test_ui(start_date, language)


if __name__ == '__main__':
    build_app()
