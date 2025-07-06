# 애플리케이션 테스트 스크립트

Write-Host "=== 애플리케이션 테스트 시작 ===" -ForegroundColor Green

# 필수 구성 요소 확인
Write-Host "1. 필수 구성 요소 확인..." -ForegroundColor Cyan

# Python 확인
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 실행 실패" -ForegroundColor Red
    exit 1
}

# 패키지 확인
Write-Host "2. Python 패키지 확인..." -ForegroundColor Cyan
$packages = @("streamlit", "yfinance", "requests", "beautifulsoup4", "pandas", "plotly")
foreach ($package in $packages) {
    try {
        python -c "import $package; print('✅ $package: OK')"
    } catch {
        Write-Host "❌ $package 패키지 누락" -ForegroundColor Red
    }
}

# Ollama 확인
Write-Host "3. Ollama 모델 확인..." -ForegroundColor Cyan
try {
    $models = ollama list
    if ($models -match "llama3.1:8b") {
        Write-Host "✅ llama3.1:8b 모델 사용 가능" -ForegroundColor Green
    } else {
        Write-Host "❌ llama3.1:8b 모델 없음" -ForegroundColor Red
        Write-Host "다음 명령어로 설치: ollama pull llama3.1:8b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ollama 실행 실패" -ForegroundColor Red
}

# 네트워크 연결 테스트
Write-Host "4. 네트워크 연결 테스트..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://finance.yahoo.com" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Yahoo Finance 연결 성공" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Yahoo Finance 연결 실패" -ForegroundColor Red
}

try {
    $response = Invoke-WebRequest -Uri "https://en.wikipedia.org" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Wikipedia 연결 성공" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Wikipedia 연결 실패" -ForegroundColor Red
}

Write-Host "테스트 완료!" -ForegroundColor Green
Write-Host "문제가 없다면 run_app.ps1을 실행하세요." -ForegroundColor Cyan
