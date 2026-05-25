import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 指令"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot.")
    
    # 未來可以在此處與資料庫互動，記錄新使用者
    
    await update.message.reply_text(
        f"你好，{user.first_name}！我是 Stockly AI Bot \n"
        "我可以幫助您分析股票並提供結合市場數據與新聞情緒的見解。\n"
        "請輸入您想查詢的股票代號，例如 /analyze AAPL"
    )

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /analyze 指令"""
    if not context.args:
        await update.message.reply_text("請提供股票代號！例如：/analyze AAPL")
        return
        
    symbol = context.args[0].upper()
    await update.message.reply_text(f"正在分析 {symbol}，這可能需要一點時間...")
    
    # TODO: 串接 data/market.py 抓取數據
    # TODO: 串接 ai/llm.py 交給 GPT 分析
    
    await update.message.reply_text(f"這裡將顯示 GPT-4o 對 {symbol} 的分析結果。")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理一般文字對話"""
    text = update.message.text
    
    # TODO: 交給 LLM 判斷使用者意圖並回覆
    
    await update.message.reply_text("我收到你的訊息了，目前我還在學習如何自然地與您對話！")
