#!/bin/bash

# vLLM 서버 관리 스크립트

case "$1" in
    "status")
        echo "=== vLLM 서버 상태 확인 ==="
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ vLLM 서버가 실행 중입니다."
            
            echo "📊 서버 정보:"
            curl -s http://localhost:8000/v1/models | jq '.data[0].id' 2>/dev/null || echo "모델 정보를 가져올 수 없습니다."
            
            echo "🔧 프로세스 정보:"
            ps aux | grep -E "(vllm|python.*api_server)" | grep -v grep
        else
            echo "❌ vLLM 서버가 실행되지 않고 있습니다."
        fi
        ;;
        
    "stop")
        echo "=== vLLM 서버 종료 ==="
        pkill -f "vllm.entrypoints.openai.api_server"
        sleep 2
        
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "❌ 서버 종료 실패"
            echo "강제 종료를 시도합니다..."
            pkill -9 -f "vllm"
        else
            echo "✅ vLLM 서버가 종료되었습니다."
        fi
        ;;
        
    "restart")
        echo "=== vLLM 서버 재시작 ==="
        $0 stop
        sleep 3
        echo "서버를 다시 시작합니다..."
        ./start_vllm.sh &
        ;;
        
    "logs")
        echo "=== vLLM 서버 로그 ==="
        tail -f vllm_server.log 2>/dev/null || echo "로그 파일을 찾을 수 없습니다."
        ;;
        
    *)
        echo "vLLM 서버 관리 스크립트"
        echo ""
        echo "사용법: $0 {status|stop|restart|logs}"
        echo ""
        echo "  status   - 서버 상태 확인"
        echo "  stop     - 서버 종료"
        echo "  restart  - 서버 재시작"
        echo "  logs     - 서버 로그 보기"
        echo ""
        echo "예시:"
        echo "  $0 status    # 현재 상태 확인"
        echo "  $0 stop      # 서버 중지"
        echo "  $0 restart   # 서버 재시작"
        ;;
esac
