#!/bin/bash
# WSL에서 vLLM 서버 실행 스크립트

echo "=== vLLM 서버 설정 및 실행 ==="

# # 가상환경 생성 및 활성화
# if [ ! -d "venv_vllm" ]; then
#     echo "📦 vLLM용 가상환경 생성 중..."
#     python3 -m venv venv_vllm
# fi

# echo "🔧 가상환경 활성화..."
# source venv_vllm/bin/activate

# # vLLM 설치
# echo "📥 vLLM 패키지 설치 중..."
# pip install --upgrade pip
# pip install vllm

# GPU 확인
echo "🔍 GPU 상태 확인..."
nvidia-smi

# 모델 다운로드 및 서버 시작
echo "🚀 vLLM 서버 시작..."
echo "모델: meta-llama/Llama-3.1-8B-Instruct"
echo "포트: 8000"
echo "종료하려면 Ctrl+C를 누르세요."

python3 -m vllm.entrypoints.openai.api_server \
  --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --dtype float16 \
  --gpu-memory-utilization 0.8 \
  --max-num-seqs 1 \
  --max-num-batched-tokens 512
