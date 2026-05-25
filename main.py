import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from db.database import init_db
from bot.handlers import start_command, analyze_command, chat_handler

# 設定日誌
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # 讀取環境變數
    load_dotenv()
    
    # 確保資料庫與資料表已建立
    init_db()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_telegram_bot_token_here":
        logger.error("錯誤：請在 .env 中填寫 TELEGRAM_BOT_TOKEN")
        return
        
    # 初始化 Application
    application = Application.builder().token(token).build()

    # 註冊指令與訊息處理器
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    # 啟動 Bot (會阻擋主執行緒直到關閉)
    logger.info("Stockly AI Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
