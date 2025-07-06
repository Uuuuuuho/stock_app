# vLLM으로 AI 포트폴리오 분석기 실행하기

## 🚀 빠른 시작 가이드

### Windows 환경에서 WSL + vLLM 사용

1. **WSL 터미널 열기**
   ```bash
   # Windows에서 WSL 실행
   wsl
   ```

2. **프로젝트 디렉토리로 이동**
   ```bash
   cd /mnt/e/work/stock_app
   ```

3. **스크립트 실행 권한 설정**
   ```bash
   chmod +x *.sh
   ```

4. **vLLM 서버 시작** (첫 번째 터미널)
   ```bash
   ./start_vllm.sh
   ```
   - 모델 다운로드 및 서버 시작 (5-10분 소요)
   - "Application startup complete" 메시지가 나올 때까지 대기

5. **서버 테스트** (두 번째 터미널)
   ```bash
   # 새 WSL 터미널에서
   cd /mnt/e/work/stock_app
   ./test_vllm.sh
   ```

6. **Streamlit 앱 실행** (두 번째 터미널에서)
   ```bash
   ./run_app_wsl.sh
   ```

7. **브라우저에서 접속**
   - http://localhost:8501

## 🛠️ 서버 관리 명령어

```bash
# 서버 상태 확인
./manage_vllm.sh status

# 서버 중지
./manage_vllm.sh stop

# 서버 재시작
./manage_vllm.sh restart
```

## 📋 주요 기능

### 1. 지능형 종목 분석
- S&P 500 전체 종목에서 목표 수익률 이상 종목 자동 필터링
- 과거 특정 시점 투자 시 현재까지의 수익률 계산

### 2. AI 기반 투자 분석
- vLLM(Llama 3.1 8B)을 활용한 투자 이유 분석
- 웹 크롤링으로 수집한 당시 뉴스 기반 분석
- Google, Naver, YouTube 뉴스 소스 통합

### 3. 시각화 및 리포트
- 일간/주간/월간 주가 차트
- 위험도 분석 (변동성 기반)
- 포트폴리오 성과 시뮬레이션
- 참고 뉴스 링크 제공

## 🔧 트러블슈팅

### vLLM 서버 문제
```bash
# GPU 메모리 부족 시
# start_vllm.sh에서 다음 수정:
--max-model-len 1024
--gpu-memory-utilization 0.6

# 더 작은 모델 사용
--model microsoft/DialoGPT-small
```

### 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501

# 프로세스 종료
pkill -f vllm
pkill -f streamlit
```

### 성능 최적화
```bash
# GPU 메모리 설정
export CUDA_VISIBLE_DEVICES=0
export VLLM_MAX_MEMORY=4GB

# CPU 버전 사용 (GPU 없는 경우)
pip install vllm[cpu]
```

## 📁 파일 구조

```
stock_app/
├── stock_research_app.py      # 메인 애플리케이션
├── requirements.txt           # 기본 패키지
├── requirements_vllm.txt      # vLLM 패키지
├── start_vllm.sh             # vLLM 서버 시작
├── test_vllm.sh              # vLLM 서버 테스트
├── run_app_wsl.sh            # WSL에서 앱 실행
├── manage_vllm.sh            # vLLM 서버 관리
├── README_WSL.md             # 상세 WSL 가이드
└── VLLM_QUICKSTART.md        # 이 파일
```

## 🎯 사용 예시

1. **목표 수익률 50% 이상 종목 찾기**
   - 사이드바에서 "목표 수익률" 50% 설정
   - "분석 시작일" 2년 전 날짜 선택
   - "주식 분석 시작" 버튼 클릭

2. **분석 결과 확인**
   - 필터링된 종목 리스트 확인
   - AI 분석 결과로 각 종목의 상승 이유 확인
   - 차트에서 성과 시각화 확인

3. **참고 자료 활용**
   - "크롤링 정보" 섹션에서 당시 뉴스 확인
   - 참고 링크를 통해 추가 정보 수집

## ⚡ 성능 요구사항

- **최소**: GTX 1660 Ti (6GB VRAM), 16GB RAM
- **권장**: RTX 3060 (12GB VRAM), 32GB RAM
- **최적**: RTX 4070+ (16GB+ VRAM), 64GB RAM

GPU가 없는 경우 CPU 버전 사용 가능하지만 속도가 느려집니다.
