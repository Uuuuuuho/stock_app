# WSL에서 vLLM으로 AI 포트폴리오 분석기 실행하기

## 🚀 시스템 요구사항

### 하드웨어
- **GPU**: NVIDIA GPU (CUDA 지원)
- **VRAM**: 최소 16GB (Llama-3.1-8B 모델용)
- **RAM**: 최소 16GB
- **저장공간**: 최소 50GB

### 소프트웨어
- **WSL2**: Windows Subsystem for Linux 2
- **Ubuntu 20.04+** (WSL 내)
- **Python 3.8+**
- **CUDA Toolkit**
- **NVIDIA Docker** (선택사항)

## 🛠️ 설치 및 설정

### 1단계: WSL2 및 Ubuntu 설치
```bash
# Windows PowerShell (관리자 권한)
wsl --install
wsl --set-default-version 2
```

### 2단계: Ubuntu에서 기본 패키지 설치
```bash
# WSL Ubuntu 터미널에서
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl jq
sudo apt install -y build-essential
```

### 3단계: NVIDIA GPU 드라이버 설정 (WSL용)
```bash
# NVIDIA Container Toolkit 설치
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
```

### 4단계: CUDA 설치
```bash
# CUDA Toolkit 설치
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-2
```

## 🚀 실행 방법

### 1단계: 프로젝트 폴더로 이동
```bash
cd /mnt/e/work/stock_app
```

### 2단계: 스크립트 실행 권한 부여
```bash
chmod +x *.sh
```

### 3단계: vLLM 서버 시작 (터미널 1)
```bash
./start_vllm.sh
```

### 4단계: Streamlit 앱 실행 (터미널 2)
```bash
./run_app_wsl.sh
```

### 5단계: 브라우저 접속
- http://localhost:8501

## 🧪 테스트 방법

### vLLM 서버 테스트
```bash
./test_vllm.sh
```

### Python 기능 테스트
```bash
source venv/bin/activate
python test_functions.py
```

## 📊 성능 최적화

### GPU 메모리 최적화
```bash
# 환경변수 설정
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### vLLM 서버 설정 최적화
```bash
# 고성능 GPU용 (A100, RTX 4090 등)
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 2 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9

# 메모리 부족시
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 1 \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.7
```

## 🔧 문제 해결

### CUDA 인식 안됨
```bash
# GPU 상태 확인
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

### 메모리 부족 오류
```bash
# 스왑 메모리 늘리기
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### vLLM 서버 연결 실패
```bash
# 포트 확인
netstat -tulpn | grep 8000

# 방화벽 확인
sudo ufw allow 8000
```

## 📁 파일 구조 (WSL 버전)
```
stock_app/
├── stock_research_app.py      # 메인 애플리케이션 (vLLM 버전)
├── requirements.txt           # 기본 패키지
├── requirements_vllm.txt      # vLLM 전용 패키지
├── start_vllm.sh             # vLLM 서버 시작 스크립트
├── run_app_wsl.sh            # WSL용 앱 실행 스크립트
├── test_vllm.sh              # vLLM 테스트 스크립트
├── test_functions.py         # Python 기능 테스트
└── README_WSL.md             # WSL 실행 가이드
```

## ⚡ 성능 벤치마크

### 예상 성능 (RTX 4090 기준)
- **모델 로딩**: 2-3분
- **첫 추론**: 3-5초
- **이후 추론**: 1-2초
- **메모리 사용량**: 14-16GB VRAM

### 모델 대안
- **더 작은 모델**: Llama-3.1-7B
- **더 빠른 모델**: Qwen2-7B-Instruct
- **양자화 모델**: Llama-3.1-8B-Instruct-AWQ
