import os
from .database import SessionLocal
from .models import SystemConfig

def get_setting(key: str, default: str = "") -> str:
    """從資料庫獲取動態設定，若無則降級使用環境變數"""
    try:
        db = SessionLocal()
        config = db.query(SystemConfig).filter(SystemConfig.key_name == key).first()
        db.close()
        if config and config.value:
            return config.value
    except Exception:
        pass
    return os.getenv(key, default)
