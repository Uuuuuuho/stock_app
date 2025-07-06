#!/bin/bash
# vLLM 서버 테스트 스크립트

echo "=== vLLM 서버 테스트 ==="

# 서버 상태 확인
echo "1. 서버 연결 확인..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ vLLM 서버 연결 성공"
else
    echo "❌ vLLM 서버 연결 실패"
    echo "서버를 먼저 시작하세요: ./start_vllm.sh"
    exit 1
fi

# 모델 정보 확인
echo "2. 모델 정보 확인..."
curl -s http://localhost:8000/v1/models | jq .

# 간단한 테스트 요청
echo "3. 테스트 요청 전송..."
curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "user", "content": "Apple 주식이 2022년에 상승한 이유를 간단히 설명해주세요."}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }' | jq .

echo "테스트 완료!"
