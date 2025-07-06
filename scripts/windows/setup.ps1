# 초기 설정 스크립트

Write-Host "=== AI 포트폴리오 분석기 초기 설정 ===" -ForegroundColor Green

# PowerShell 실행 정책 확인
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "⚠️ PowerShell 실행 정책이 제한되어 있습니다." -ForegroundColor Yellow
    Write-Host "다음 명령어를 관리자 권한으로 실행하세요:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    exit 1
}

# 필수 소프트웨어 설치 가이드
Write-Host "📋 필수 소프트웨어 설치 확인..." -ForegroundColor Cyan

# Python 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 미설치" -ForegroundColor Red
    Write-Host "설치 방법:" -ForegroundColor Yellow
    Write-Host "1. https://www.python.org/downloads/ 접속" -ForegroundColor White
    Write-Host "2. Python 3.8+ 다운로드 및 설치" -ForegroundColor White
    Write-Host "3. 설치 시 'Add Python to PATH' 체크" -ForegroundColor White
}

# Ollama 확인
try {
    $ollamaVersion = ollama version 2>&1
    Write-Host "✅ Ollama: $ollamaVersion" -ForegroundColor Green
    
    # llama3.1:8b 모델 확인
    $models = ollama list 2>&1
    if ($models -match "llama3.1:8b") {
        Write-Host "✅ llama3.1:8b 모델 설치됨" -ForegroundColor Green
    } else {
        Write-Host "⚠️ llama3.1:8b 모델 미설치" -ForegroundColor Yellow
        Write-Host "다음 명령어로 설치하세요: ollama pull llama3.1:8b" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Ollama 미설치" -ForegroundColor Red
    Write-Host "설치 방법:" -ForegroundColor Yellow
    Write-Host "1. https://ollama.ai/ 접속" -ForegroundColor White
    Write-Host "2. Windows용 Ollama 다운로드 및 설치" -ForegroundColor White
    Write-Host "3. 설치 후 'ollama pull llama3.1:8b' 실행" -ForegroundColor White
}

Write-Host "`n설정 완료 후 'run_app.ps1' 또는 'run_app.bat'을 실행하세요." -ForegroundColor Green
