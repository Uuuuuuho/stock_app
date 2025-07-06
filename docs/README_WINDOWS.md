# Windows에서 AI 포트폴리오 분석기 실행하기

## 🚀 빠른 시작

### 1단계: 필수 소프트웨어 설치

#### Python 설치
1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.8+ 다운로드
2. 설치 시 **"Add Python to PATH"** 반드시 체크
3. 설치 확인: `python --version`

#### Ollama 설치
1. [Ollama 공식 사이트](https://ollama.ai/)에서 Windows용 다운로드
2. 설치 후 모델 다운로드:
   ```powershell
   ollama pull llama3.1:8b
   ```

### 2단계: 프로젝트 실행

#### PowerShell 방법 (권장)
```powershell
# 실행 정책 설정 (관리자 권한 필요)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 초기 설정 확인
.\setup.ps1

# 앱 실행
.\run_app.ps1
```

#### 배치파일 방법 (대안)
```cmd
# 앱 실행
run_app.bat
```

### 3단계: 브라우저 접속
- 자동으로 브라우저가 열리거나
- 수동으로 http://localhost:8501 접속

## 🔧 문제 해결

### PowerShell 실행 정책 오류
```powershell
# 현재 사용자만 허용
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 임시 허용
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Python 경로 오류
1. 환경변수 PATH에 Python 경로 추가
2. Python 재설치 (Add to PATH 체크)

### Ollama 연결 오류
1. Ollama 서비스 실행 확인
2. 모델 다운로드 확인: `ollama list`

### 패키지 설치 오류
```powershell
# pip 업그레이드
python -m pip install --upgrade pip

# 수동 패키지 설치
pip install streamlit yfinance requests beautifulsoup4 matplotlib pandas plotly
```

## 📁 파일 구조
```
stock_app/
├── stock_research_app.py    # 메인 애플리케이션
├── requirements.txt         # Python 패키지 목록
├── run_app.ps1             # PowerShell 실행 스크립트
├── run_app.bat             # 배치 실행 스크립트
├── setup.ps1               # 초기 설정 스크립트
├── test_app.ps1            # PowerShell 테스트 스크립트
├── test_functions.py       # Python 기능 테스트
└── README_WINDOWS.md       # Windows 실행 가이드
```

## 🎯 사용법
1. 좌측 사이드바에서 분석 조건 설정
2. "🚀 분석 실행" 버튼 클릭
3. 결과 테이블과 차트 확인
4. AI 분석 결과 확인

## ⚡ 성능 최적화
- 첫 실행 시 S&P500 데이터 로딩으로 시간 소요
- Ollama 모델 로딩으로 AI 분석 시간 소요
- 안정적인 인터넷 연결 필요 (웹 크롤링)

## 🧪 테스트 방법
```powershell
# 환경 테스트
.\test_app.ps1

# 기능 테스트
python test_functions.py
```
