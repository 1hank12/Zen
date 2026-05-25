from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)

# 初始化 OpenAI 非同步客戶端
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def resolve_stock_symbol(query: str) -> str:
    """將使用者的任意輸入（如中文名稱、錯字）轉換為標準股票代碼"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a stock symbol resolver. The user gives a company name. Return ONLY the standard ticker symbol. If it's a Taiwan company, return only the digits (e.g., 2330). If it's a US company, return only the letters (e.g., AAPL). No punctuation or other words."},
                {"role": "user", "content": query}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip().upper()
    except Exception as e:
        logger.error(f"Error resolving symbol: {e}")
        return query.strip().upper()

async def get_investment_advice(symbol: str, market_data: dict, news_data: list) -> str:
    """
    將市場數據與新聞資料交給 GPT-4o 進行分析，回傳分析結果。
    """
    try:
        # 建構適合雙端查核系統的 System Prompt
        system_prompt = (
            "你是一個專業的量化金融AI助理，負責根據數據與新聞提供中立的見解。\n\n"
            "【資料查核任務】在使用者提供的「多重來源市場數據」中，包含了兩組來自不同 API 供應商的報價 (如 TWSE 與 Fugle，或 Polygon 與 Alpha_Vantage)。\n"
            "請您在分析一開始，先為這兩組來源進行交叉比對，判斷資料是否一致。若有其中一方遺失數值或是報價存在落差，請根據常理判斷並在報告中特別加粗註明，以展現機構級的嚴謹度。\n"
        )
        
        user_content = f"請分析股票 {symbol}。\n\n【多重來源市場數據】: {market_data}\n\n【近期繁體中文新聞】: {news_data}"
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return "抱歉，在分析過程中發生了一些錯誤。"

async def chat_with_ai(user_text: str) -> str:
    """自由對話：讓 AI 使用自然語言回覆財經問題"""
    try:
        system_prompt = (
            "您是一位具備數十年經驗的華爾街量化金融分析師。您的任務是為使用者解答任何「股票、ETF、匯率或財經知識」的問題。"
            "請用繁體中文、淺顯易懂但具備專業深度的口吻回答。如果是比較型的問題 (例如 0050 vs VOO)，請客觀分析優劣勢與適用對象。"
        )
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.6,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {e}")
        return "不好意思，我的連線似乎出了一點狀況，請稍後再試！"
