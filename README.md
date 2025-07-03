# AI 기반 종목 추천 리서치 도우미

## 소개

이 프로젝트는 지정한 날짜에 미국 주식(S&P500 주요 종목)에 투자했을 때 10% 이상의 수익률을 기록한 종목을 자동으로 분석하고, 각 종목의 상승 이유를 웹 크롤링 및 LLM(로컬 Ollama) 요약을 통해 시각적으로 보여주는 Streamlit 기반 리서치 도우미 앱입니다.

---

## 주요 기능

- **날짜 및 추천 종목 수 입력**: 원하는 투자 날짜와 추천받을 종목 개수 입력
- **수익률 계산**: yfinance로 과거 시세 조회, 10% 이상 수익률 종목 필터링
- **웹 정보 수집**: 각 종목별로 해당 날짜 기준 뉴스/정보 3건 크롤링 (Google API 미사용)
- **LLM 요약**: Ollama의 llama3 모델로 종목별 상승 이유 3줄 요약
- **시각화**: 수익률 바 차트, 종목 요약 테이블, 추천 사유 요약 테이블 제공

---

## 실행 방법

1. **필수 패키지 설치**

```bash
pip install streamlit yfinance requests beautifulsoup4 matplotlib pandas
```

2. **Ollama 설치 및 llama3 모델 준비**

- [Ollama 공식 사이트](https://ollama.com/)에서 설치
- 터미널에서 모델 다운로드:

```bash
ollama pull llama3
```

3. **앱 실행**

```bash
streamlit run stock_research_app.py
```

4. **웹 브라우저에서 UI 사용**

- 날짜와 추천 종목 수 입력 후 "분석 실행" 클릭
- 수익률 상위 종목, 요약 테이블, 추천 사유 요약 확인

---

## 폴더 구조

```
stock_app/
  ├─ stock_research_app.py
  └─ README.md
```

---

## 참고 및 주의사항

- 크롤링은 Bing 검색을 사용하며, 네트워크 환경에 따라 결과가 다를 수 있습니다.
- Ollama가 정상적으로 설치되어 있어야 LLM 요약 기능이 동작합니다.
- 예시 티커(AAPL, MSFT, GOOGL, AMZN, TSLA)만 포함되어 있으며, 필요시 확장 가능합니다.

---

## 라이선스

MIT License
