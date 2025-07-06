#!/bin/bash
# WSL에서 Streamlit 앱 실행 스크립트

echo "=== AI 포트폴리오 분석기 (WSL 버전) ==="

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되지 않았습니다."
    echo "설치 명령어: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "✅ Python3: $(python3 --version)"

# 가상환경 활성화 (기존 stock-py 환경 사용)
echo "🔧 가상환경 활성화..."
if [ -d "/home/$USER/work/stock-py" ]; then
    source /home/$USER/work/stock-py/bin/activate
    echo "✅ stock-py 가상환경 활성화됨"
else
    echo "❌ stock-py 가상환경을 찾을 수 없습니다."
    echo "경로를 확인하고 다시 시도하세요: /home/$USER/work/stock-py"
    exit 1
fi

# 패키지 설치
echo "📥 필요한 패키지 설치 중..."
pip install -r requirements.txt

# vLLM 서버 상태 확인
echo "🔍 vLLM 서버 연결 확인..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ vLLM 서버 연결 성공"
else
    echo "⚠️ vLLM 서버가 실행되지 않았습니다."
    echo "다른 터미널에서 './start_vllm.sh'를 먼저 실행하세요."
fi

# Streamlit 앱 실행
echo "🚀 Streamlit 앱 시작..."
echo "브라우저에서 http://localhost:8501 으로 접속하세요."
echo "종료하려면 Ctrl+C를 누르세요."

# 프로젝트 루트에서 실행
cd /mnt/e/work/stock_app
streamlit run src/app.py
