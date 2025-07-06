# 간단한 테스트 스크립트 (Python 없이도 실행 가능)

Write-Host "=== 시스템 환경 확인 ===" -ForegroundColor Green

# 1. 운영체제 정보
Write-Host "`n1. 시스템 정보:" -ForegroundColor Cyan
Write-Host "   OS: $([System.Environment]::OSVersion.VersionString)" -ForegroundColor White
Write-Host "   PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor White

# 2. 네트워크 연결 테스트
Write-Host "`n2. 네트워크 연결 테스트:" -ForegroundColor Cyan

$sites = @(
    @{Name="Yahoo Finance"; Url="https://finance.yahoo.com"},
    @{Name="Wikipedia"; Url="https://en.wikipedia.org"},
    @{Name="Google"; Url="https://www.google.com"},
    @{Name="PyPI"; Url="https://pypi.org"}
)

foreach ($site in $sites) {
    try {
        $response = Invoke-WebRequest -Uri $site.Url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($site.Name): 연결 성공" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ❌ $($site.Name): 연결 실패" -ForegroundColor Red
    }
}

# 3. 필수 프로그램 확인
Write-Host "`n3. 필수 프로그램 확인:" -ForegroundColor Cyan

$programs = @("python", "py", "pip", "ollama", "git")
foreach ($program in $programs) {
    try {
        $null = Get-Command $program -ErrorAction Stop
        Write-Host "   ✅ $program: 설치됨" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $program: 미설치" -ForegroundColor Red
    }
}

# 4. 파일 존재 확인
Write-Host "`n4. 프로젝트 파일 확인:" -ForegroundColor Cyan

$files = @(
    "stock_research_app.py",
    "requirements.txt",
    "run_app.ps1",
    "run_app.bat"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file: 존재" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file: 없음" -ForegroundColor Red
    }
}

# 5. 권장사항
Write-Host "`n=== 권장사항 ===" -ForegroundColor Yellow

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "🐍 Python 설치 필요:" -ForegroundColor Red
    Write-Host "   방법 1: install_python.ps1 실행 (관리자 권한)" -ForegroundColor White
    Write-Host "   방법 2: https://www.python.org/downloads/ 에서 수동 설치" -ForegroundColor White
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "🤖 Ollama 설치 필요:" -ForegroundColor Red
    Write-Host "   https://ollama.ai/ 에서 다운로드" -ForegroundColor White
}

Write-Host "`n모든 준비가 완료되면 'run_app.ps1' 또는 'run_app.bat'을 실행하세요!" -ForegroundColor Green
