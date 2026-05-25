import logging
from telegram import Update
from telegram.ext import ContextTypes

from db.database import SessionLocal
from db.models import User
from data.market import get_stock_data, get_stock_news, normalize_symbol
from ai.llm import get_investment_advice, resolve_stock_symbol

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 指令"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot.")
    
    # 紀錄新使用者進資料庫 (Supabase 或 SQLite)
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.telegram_id == str(user.id)).first()
        if not db_user:
            new_user = User(telegram_id=str(user.id))
            db.add(new_user)
            db.commit()
            logger.info(f"成功將新使用者 {user.id} 存入資料庫！")
    except Exception as e:
        logger.error(f"資料庫寫入錯誤: {e}")
    finally:
        db.close()
    
    await update.message.reply_text(
        f"你好，{user.first_name}！我是 Stockly AI Bot 🤖\n"
        "我已經將您的資料安全儲存。\n\n"
        "我可以幫助您分析股票並提供結合市場數據與新聞情緒的見解。\n"
        "您可以輸入代號或「中文名稱」，例如：/analyze 蘋果"
    )

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /analyze 指令"""
    if not context.args:
        await update.message.reply_text("請提供想查詢的公司！例如：/analyze 蘋果 或 /analyze 台積電")
        return
        
    query = " ".join(context.args)
    status_message = await update.message.reply_text(f"正在辨識「{query}」的股票代碼... 💡")
    
    # 透過 GPT 解析出標準代碼 (例如 "蘋果" -> "AAPL")
    raw_symbol = await resolve_stock_symbol(query)
    normalized_symbol, market_type = normalize_symbol(raw_symbol)
    
    await status_message.edit_text(f"🌍 偵測為【{market_type}】 ({raw_symbol})\n正在透過官方專業 API 搜尋 {normalized_symbol} 的數據與在地新聞... ⏳")
    
    # 1. 抓取數據與新聞 (透過雙軌 API 分流：台股走 TWSE、美股走 Alpha Vantage)
    market_data = get_stock_data(normalized_symbol, market_type)
    news_data = get_stock_news(raw_symbol, market_type) # 新聞用沒有 .TW 的字串去 Google 搜尋比較精準
    
    if not market_data or market_data.get('current_price') is None:
        await status_message.edit_text(f"找不到 {normalized_symbol} 的相關數據，請確認公司名稱是否正確上市。")
        return
        
    await status_message.edit_text(f"【{market_type}】數據收集完畢！正在交由 OpenAI GPT-4o 進行深入分析... 🧠\n(這大約需要 10-15 秒)")
    
    # 2. 呼叫 OpenAI
    analysis = await get_investment_advice(normalized_symbol, market_data, news_data)
    
    # 3. 回傳結果
    await status_message.edit_text(analysis)

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理一般文字對話"""
    await update.message.reply_text("目前我只聽得懂 /analyze 這句指令喔！例如：/analyze 微軟 或 /analyze 輝達")
