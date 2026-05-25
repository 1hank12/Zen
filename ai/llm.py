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
        system_prompt = (
            "您是一位頂尖的華爾街量化金融分析師 (Quants)。負責根據數據與新聞提供極其嚴謹、具備高度專業深度的見解。\n\n"
            "請在分析中帶入量化思維（如波動風險、估值模型、Beta值、市場情緒因子等），拒絕無憑無據的市井言論，展現出頂尖分析師的冷靜、客觀與數據導向。\n"
            "【資料查核任務】在使用者提供的「多重來源市場數據」中，包含了來自不同 API 供應商的報價 (如 TWSE 與 Fugle，或 Polygon 與 Alpha_Vantage)。\n"
            "請在分析開頭，為這兩組來源進行交叉比對是否一致。若有落差，請根據常理判斷並在報告中醒目註明，以展現機構級的嚴謹度。\n"
        )
        
        user_content = f"請分析股票 {symbol}。\n\n【多重來源市場數據】: {market_data}\n\n【近期繁體中文新聞】: {news_data}"
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return "抱歉，分析過程中核心運算模組發生錯誤。"

async def chat_with_ai(user_text: str) -> str:
    """自由對話：讓 AI 使用自然語言回覆財經問題"""
    try:
        system_prompt = (
            "您是一位具備數十年經驗的頂尖華爾街量化金融分析師（Quantitative Analyst）。\n"
            "您的任務是為使用者解答「股票、ETF、總體經濟或量化交易」等問題。\n"
            "請展現極高的專業度與嚴謹的邏輯，講話冷靜客觀。回答時請多運用專業量化指標（如夏普值 Sharpe Ratio、Beta 係數、波動率、最大回撤、Alpha 因子等）進行論述。\n"
            "特別注意：在解釋較深的量化或財經概念時，請先給出一個「設計師也能聽懂的生活/系統類比」，再進入技術細節，這能彰顯您頂級分析師的溝通功力。\n"
            "請全程使用繁體中文，拒絕給出似是而非的玄學分析。"
        )
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {e}")
        return "不好意思，量化分析引擎目前連線異常，請稍後再試！"
