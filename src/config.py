# Configuration for stock research app

# vLLM model and API
MODEL_NAME = "google/gemma-2b-it"
VLLM_API_URL = "http://localhost:8000/v1/chat/completions"

# LLM parameters
MAX_TOKENS = 250  # Increased for more detailed analysis
TEMPERATURE = 0.7

# Supported UI languages (Korean and English only)
CONFIG_LANGUAGES = ["한국어", "English"]

# Number of references to review from each source
NUM_REFERENCES = 15

# Deep Learning Model recommendations based on stock characteristics
DL_MODEL_RECOMMENDATIONS = {
    "high_volatility": {
        "model": "LSTM (Long Short-Term Memory)",
        "reason": "높은 변동성 종목에 적합한 시계열 패턴 학습"
    },
    "low_volatility": {
        "model": "GRU (Gated Recurrent Unit)",
        "reason": "안정적인 종목의 장기 트렌드 예측에 효과적"
    },
    "high_return": {
        "model": "Transformer with Attention",
        "reason": "급격한 가격 변동과 복잡한 패턴 인식에 특화"
    },
    "medium_return": {
        "model": "CNN-LSTM Hybrid",
        "reason": "중간 수준 수익률의 다중 시간대 패턴 분석에 적합"
    }
}
