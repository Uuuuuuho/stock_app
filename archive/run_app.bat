@echo off
REM Windows 배치 파일 (PowerShell 실행 권한이 없는 경우)

echo === AI 포트폴리오 분석기 시작 ===

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo 다운로드: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Ollama 설치 확인
ollama version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama가 설치되지 않았습니다.
    echo 다운로드: https://ollama.ai/
    echo 설치 후 'ollama pull llama3.1:8b' 명령어를 실행하세요.
    pause
    exit /b 1
)

REM 가상환경 생성
if not exist "venv" (
    echo 📦 가상환경 생성 중...
    python -m venv venv
)

REM 가상환경 활성화
echo 🔧 가상환경 활성화...
call venv\Scripts\activate.bat

REM 패키지 설치
echo 📥 필요한 패키지 설치 중...
pip install -r requirements.txt

REM Streamlit 앱 실행
echo 🚀 Streamlit 앱 시작...
echo 브라우저에서 http://localhost:8501 으로 접속하세요.
echo 종료하려면 Ctrl+C를 누르세요.

streamlit run stock_research_app.py
pause
