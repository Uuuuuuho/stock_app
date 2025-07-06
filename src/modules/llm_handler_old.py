import requests
from config import MODEL_NAME, VLLM_API_URL, MAX_TOKENS, TEMPERATURE

def run_llm(ticker, date, return_pct, articles, language="한국어"):
    """Request analysis from vLLM API."""
    # Language-specific prompts for better accuracy
    language_prompts = {
        "한국어": f"""
{date}에 {ticker}에 투자했다면 오늘까지 수익률은 {return_pct:.2f}%입니다.
주요 기사:
{articles}

이 종목이 상승한 이유를 한국어로 3줄 이내로 정리해주세요.
반드시 한국어로만 답변해주세요.
""",
        "English": f"""
If you invested in {ticker} on {date}, the return would be {return_pct:.2f}% until today.
Key articles:
{articles}

Please summarize in English why this stock rose in 3 lines or less.
Please respond only in English.
""",
        "日本語": f"""
{date}に{ticker}に投資していたら、今日までの収益率は{return_pct:.2f}%です。
主要記事:
{articles}

この銘柄が上昇した理由を日本語で3行以内にまとめてください。
必ず日本語のみで回答してください。
""",
        "中文": f"""
如果在{date}投资{ticker}，到今天的收益率将是{return_pct:.2f}%。
主要文章：
{articles}

请用中文在3行内总结这只股票上涨的原因。
请只用中文回答。
""",
        "Deutsch": f"""
Wenn Sie am {date} in {ticker} investiert hätten, wäre die Rendite bis heute {return_pct:.2f}%.
Hauptartikel:
{articles}

Bitte fassen Sie auf Deutsch in 3 Zeilen oder weniger zusammen, warum diese Aktie gestiegen ist.
Bitte antworten Sie nur auf Deutsch.
"""
    }
    
    # Get appropriate prompt for selected language
    prompt = language_prompts.get(language, language_prompts["한국어"])
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE
    }
    try:
        res = requests.post(VLLM_API_URL, json=payload, headers={"Content-Type":"application/json"}, timeout=30)
        if res.status_code == 200:
            data = res.json()
            summary = data['choices'][0]['message']['content'].strip()
            return summary, prompt
        else:
            print(f"LLM Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"LLM request failed: {e}")
    return "정보 없음", prompt
