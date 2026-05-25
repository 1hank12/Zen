import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def get_stock_data(symbol: str) -> dict:
    """
    使用 yfinance 抓取股票的基本資料與近期價格
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        info = ticker.info
        
        result = {
            "current_price": info.get("currentPrice"),
            "pe_ratio": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "recent_prices": hist['Close'].tail(5).to_dict() # 最近五天收盤價
        }
        return result
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return {}

def get_stock_news(symbol: str) -> list:
    """
    獲取股票相關新聞 (暫代實作，未來可串接 NewsAPI)
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        
        # 取出前3則新聞標題
        return [item['title'] for item in news[:3]]
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return []
