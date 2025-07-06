# Python 자동 설치 및 설정 스크립트

Write-Host "=== Python 자동 설치 및 애플리케이션 설정 ===" -ForegroundColor Green

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️ 관리자 권한이 필요합니다. PowerShell을 관리자로 실행해주세요." -ForegroundColor Yellow
    Write-Host "또는 수동으로 Python을 설치하세요: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

# Chocolatey 설치 확인
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Chocolatey 설치 중..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Python 설치
Write-Host "🐍 Python 설치 중..." -ForegroundColor Yellow
choco install python -y

# 환경 변수 새로고침
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Python 설치 확인
try {
    $pythonVersion = python --version
    Write-Host "✅ Python 설치 완료: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 설치 실패. 수동 설치가 필요합니다." -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

# pip 업그레이드
Write-Host "📦 pip 업그레이드 중..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Ollama 설치 (선택사항)
$installOllama = Read-Host "Ollama를 자동으로 설치하시겠습니까? (y/n)"
if ($installOllama -eq "y" -or $installOllama -eq "Y") {
    Write-Host "🤖 Ollama 설치 중..." -ForegroundColor Yellow
    choco install ollama -y
    
    Write-Host "📥 llama3.1:8b 모델 다운로드 중..." -ForegroundColor Yellow
    ollama pull llama3.1:8b
}

Write-Host "✅ 설정 완료! 이제 'run_app.ps1'을 실행할 수 있습니다." -ForegroundColor Green
