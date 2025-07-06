# Stock Research App 실행 스크립트

Write-Host "=== AI 포트폴리오 분석기 시작 ===" -ForegroundColor Green

# Python 설치 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 버전: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Python이 설치되지 않았습니다. Python 3.8+ 설치가 필요합니다." -ForegroundColor Red
    Write-Host "다운로드: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Ollama 설치 확인
try {
    $ollamaVersion = ollama version 2>&1
    Write-Host "Ollama 버전: $ollamaVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Ollama가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다운로드: https://ollama.ai/" -ForegroundColor Yellow
    Write-Host "설치 후 'ollama pull llama3.1:8b' 명령어를 실행하세요." -ForegroundColor Yellow
    exit 1
}

# 가상환경 생성 및 활성화
if (-not (Test-Path ".\venv")) {
    Write-Host "📦 가상환경 생성 중..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "🔧 가상환경 활성화..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 필요한 패키지 설치
Write-Host "📥 필요한 패키지 설치 중..." -ForegroundColor Yellow
pip install -r requirements.txt

# Streamlit 앱 실행
Write-Host "🚀 Streamlit 앱 시작..." -ForegroundColor Green
Write-Host "브라우저에서 http://localhost:8501 으로 접속하세요." -ForegroundColor Cyan
Write-Host "종료하려면 Ctrl+C를 누르세요." -ForegroundColor Yellow

streamlit run stock_research_app.py
