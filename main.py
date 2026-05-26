import os
import logging
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from db.database import init_db, SessionLocal
from db.models import User, SystemConfig
from bot.handlers import start_command, analyze_command, chat_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
init_db()

# ---- 機器人全域變數 ----
token = os.getenv("TELEGRAM_BOT_TOKEN")
application = Application.builder().token(token).build()
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("analyze", analyze_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 啟動時一併啟動 Telegram 機器人 (非阻塞模式, Polling)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("Telegram Bot (Polling) & Admin Dashboard APIs are LIVE!")
    yield
    # FastAPI 關閉時安全停止機器人
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)

# ---- 後台 API 端點 ----
@app.get("/api/stats")
async def get_stats():
    db = SessionLocal()
    user_count = db.query(User).count()
    db.close()
    return {"status": "online", "users": user_count}

@app.get("/api/config")
async def get_config():
    db = SessionLocal()
    configs = db.query(SystemConfig).all()
    # 給予預設值清單回傳前端
    result = {}
    for c in configs:
        result[c.key_name] = c.value
    db.close()
    
    # 確保預設欄位存在
    default_keys = ["SYSTEM_PROMPT", "FUGLE_API_KEY", "POLYGON_API_KEY"]
    for k in default_keys:
        if k not in result:
            result[k] = ""
            
    return {"configs": result}

class ConfigUpdate(BaseModel):
    key_name: str
    value: str

@app.post("/api/config")
async def update_config(payload: ConfigUpdate):
    db = SessionLocal()
    config = db.query(SystemConfig).filter(SystemConfig.key_name == payload.key_name).first()
    if config:
        config.value = payload.value
    else:
        config = SystemConfig(key_name=payload.key_name, value=payload.value)
        db.add(config)
    db.commit()
    db.close()
    return {"status": "success", "message": f"{payload.key_name} updated successfully!"}

# 掛載靜態網頁前端
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # 透過 uvicorn 啟動 FastAPI，取代原本陽春的 heart_check server
    uvicorn.run(app, host="0.0.0.0", port=port)
