import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
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

class HealthCheckHandler(BaseHTTPRequestHandler):
    """雲端健康檢查器：用來欺騙 Render 這是一台正常的網頁伺服器"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Stockly AI Bot is alive and running 24/7 on the Cloud!")
        
    def log_message(self, format, *args):
        # 關閉 ping 日誌以免洗版
        pass

def start_health_server():
    """在背景執行緒啟動心跳網頁"""
    try:
        # Render 預設使用環境變數 PORT，若無則 fallback 到 8080
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"成功啟動心跳防護網頁，綁定 Port {port}")
    except Exception as e:
        logger.error(f"心跳伺服器啟動失敗: {e}")

def main():
    # 讀取環境變數 (本地端用，雲端會在介面上設定)
    load_dotenv()
    
    # 啟動心跳頁面
    start_health_server()
    
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
    logger.info("Stockly AI Bot is starting in polling mode...")
    application.run_polling()

if __name__ == "__main__":
    main()
