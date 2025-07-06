import requests
from config import MODEL_NAME, VLLM_API_URL, MAX_TOKENS, TEMPERATURE

def check_vllm_server():
    """Check if vLLM server is running and accessible."""
    try:
        # Try to ping the server health endpoint
        health_url = VLLM_API_URL.replace('/v1/chat/completions', '/health')
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            return True, "vLLM 서버 연결 성공"
        else:
            return False, f"vLLM 서버 응답 오류: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"vLLM 서버 연결 실패: {VLLM_API_URL}에 연결할 수 없습니다"
    except requests.exceptions.Timeout:
        return False, "vLLM 서버 연결 시간 초과"
    except Exception as e:
        return False, f"vLLM 서버 확인 중 오류: {str(e)}"

def test_vllm_simple():
    """Test vLLM with a simple request."""
    test_payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": "Hello, respond with 'Test successful'"}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            VLLM_API_URL, 
            json=test_payload, 
            headers={"Content-Type": "application/json"}, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return True, f"테스트 성공: {content}"
        else:
            return False, f"테스트 실패: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"테스트 중 오류: {str(e)}"

def run_llm(ticker, date, return_pct, articles, language="한국어"):
    """Request analysis from vLLM API with enhanced content handling."""
    
    # Check if we have real articles or fallback content
    has_fallback = any("[FALLBACK]" in article for article in articles)
    has_limited_data = len([a for a in articles if not a.startswith("[FALLBACK]")]) < 3
    
    # Format articles for better LLM processing
    formatted_articles = []
    for i, article in enumerate(articles[:10], 1):
        if article and len(article.strip()) > 5:
            formatted_articles.append(f"{i}. {article}")
    
    articles_text = "\n".join(formatted_articles) if formatted_articles else "Limited market information available"
    
    # Language-specific prompts with enhanced context
    language_prompts = {
        "한국어": f"""
{date}에 {ticker}에 투자했다면 오늘까지 수익률은 {return_pct:.2f}%입니다.

수집된 정보:
{articles_text}

{"⚠️ 주의: 제한된 뉴스 정보로 인해 일반적인 투자 분석을 포함합니다." if has_fallback or has_limited_data else ""}

이 종목의 수익률 발생 요인을 한국어로 3-4줄로 분석해주세요. 
구체적인 시장 동향, 기업 실적, 또는 섹터 영향을 포함하여 설명해주세요.
반드시 한국어로만 답변해주세요.
""",
        "English": f"""
If you invested in {ticker} on {date}, the return would be {return_pct:.2f}% until today.

Collected Information:
{articles_text}

{"⚠️ Note: Limited news data available, general investment analysis included." if has_fallback or has_limited_data else ""}

Please analyze the factors behind this stock's return in English within 3-4 lines.
Include specific market trends, company performance, or sector impacts in your explanation.
Please respond only in English.
""",
        "日本語": f"""
{date}に{ticker}に投資していたら、今日までの収益率は{return_pct:.2f}%です。

収集された情報：
{articles_text}

{"⚠️ 注意：限られたニュース情報のため、一般的な投資分析を含みます。" if has_fallback or has_limited_data else ""}

この銘柄の収益率発生要因を日本語で3-4行で分析してください。
具体的な市場動向、企業業績、またはセクター影響を含めて説明してください。
必ず日本語のみで回答してください。
""",
        "中文": f"""
如果在{date}投资{ticker}，到今天的收益率将是{return_pct:.2f}%。

收集的信息：
{articles_text}

{"⚠️ 注意：由于新闻信息有限，包含一般投资分析。" if has_fallback or has_limited_data else ""}

请用中文在3-4行内分析这只股票收益率的产生因素。
请在解释中包含具体的市场趋势、公司业绩或行业影响。
请只用中文回答。
""",
        "Deutsch": f"""
Wenn Sie am {date} in {ticker} investiert hätten, wäre die Rendite bis heute {return_pct:.2f}%.

Gesammelte Informationen:
{articles_text}

{"⚠️ Hinweis: Begrenzte Nachrichtendaten verfügbar, allgemeine Investitionsanalyse enthalten." if has_fallback or has_limited_data else ""}

Bitte analysieren Sie die Faktoren hinter der Rendite dieser Aktie auf Deutsch in 3-4 Zeilen.
Beinhalten Sie spezifische Markttrends, Unternehmensleistung oder Branchenauswirkungen in Ihrer Erklärung.
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
        print(f"🔄 vLLM 요청 시작 - Ticker: {ticker}, Language: {language}")
        print(f"📊 Articles count: {len(articles)}, Has fallback: {has_fallback}")
        print(f"🌐 API URL: {VLLM_API_URL}")
        print(f"🤖 Model: {MODEL_NAME}")
        
        res = requests.post(VLLM_API_URL, json=payload, headers={"Content-Type":"application/json"}, timeout=30)
        print(f"📡 vLLM Response Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ vLLM Response received successfully")
            summary = data['choices'][0]['message']['content'].strip()
            print(f"📝 Summary length: {len(summary)} characters")
            
            # Add disclaimer if using fallback content
            if has_fallback or has_limited_data:
                disclaimer_map = {
                    "한국어": "\n\n※ 제한된 뉴스 데이터로 인한 일반적 분석입니다.",
                    "English": "\n\n※ General analysis due to limited news data.",
                    "日本語": "\n\n※ 限られたニュースデータによる一般的な分析です。",
                    "中文": "\n\n※ 由于新闻数据有限的一般分析。",
                    "Deutsch": "\n\n※ Allgemeine Analyse aufgrund begrenzter Nachrichtendaten."
                }
                disclaimer = disclaimer_map.get(language, disclaimer_map["한국어"])
                summary += disclaimer
                print(f"⚠️ Added disclaimer for limited data")
            
            return summary, prompt
        else:
            error_msg = f"LLM Error {res.status_code}: {res.text}"
            print(f"❌ {error_msg}")
            return error_msg, prompt
    except Exception as e:
        error_msg = f"LLM request failed: {e}"
        print(f"💥 {error_msg}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return error_msg, prompt
    
    # Return language-appropriate fallback
    fallback_map = {
        "한국어": "분석 정보가 제한적입니다. 투자 전 추가 리서치를 권합니다.",
        "English": "Limited analysis information available. Additional research recommended before investment.",
        "日本語": "分析情報が限られています。投資前に追加調査をお勧めします。",
        "中文": "分析信息有限。建议投资前进行额外研究。",
        "Deutsch": "Begrenzte Analyseinformationen verfügbar. Zusätzliche Recherche vor Investition empfohlen."
    }
    fallback = fallback_map.get(language, fallback_map["한국어"])
    return fallback, prompt
