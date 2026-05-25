from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)

# 初始化 OpenAI 非同步客戶端
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_investment_advice(symbol: str, market_data: dict, news_data: list) -> str:
    """
    將市場數據與新聞資料交給 GPT-4o 進行分析，回傳分析結果。
    """
    try:
        # TODO: 建構適合投資分析的 System Prompt 與 User Prompt
        system_prompt = "你是一個專業的量化金融AI助理，負責根據數據與新聞提供中立的見解。"
        
        user_content = f"請分析股票 {symbol}。\n\n市場數據: {market_data}\n\n近期新聞: {news_data}"
        
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
