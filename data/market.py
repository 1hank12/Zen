import logging
import requests
import os
from bs4 import BeautifulSoup
import yfinance as yf

logger = logging.getLogger(__name__)

def normalize_symbol(symbol: str) -> tuple[str, str]:
    symbol = symbol.strip().upper()
    if symbol.isdigit():
        return symbol, "台股"
    return symbol, "美股"

def _fetch_twse_data(symbol: str) -> dict:
    try:
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        res = requests.get(url, timeout=10)
        data = res.json()
        target = next((item for item in data if item.get("Code") == symbol), None)
        if not target: return {}
        return {
            "current_price": float(target.get("ClosingPrice", 0)),
            "pe_ratio": float(target.get("PeRatio", 0)) if target.get("PeRatio") else "N/A"
        }
    except Exception as e:
        logger.error(f"TWSE Error: {e}")
        return {}

def _fetch_fugle_data(symbol: str) -> dict:
    apikey = os.getenv("FUGLE_API_KEY")
    if not apikey or "修改成您" in apikey: return {}
    try:
        url = f"https://api.fugle.tw/marketdata/v0.3/intraday/quote?symbolId={symbol}&apiToken={apikey}"
        res = requests.get(url, timeout=10)
        data = res.json()
        quote = data.get("data", {}).get("quote", {})
        if not quote: return {}
        cp = float(quote.get("trade", {}).get("price", 0))
        if cp == 0: cp = float(quote.get("priceHigh", {}).get("price", 0))
        return {"current_price": cp}
    except Exception as e:
        logger.error(f"Fugle Error: {e}")
        return {}

def _fetch_polygon_data(symbol: str) -> dict:
    apikey = os.getenv("POLYGON_API_KEY")
    if not apikey or "修改成您" in apikey: return {}
    try:
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}?apiKey={apikey}"
        res = requests.get(url, timeout=10)
        data = res.json()
        ticker = data.get("ticker", {})
        if not ticker: return {}
        cp = float(ticker.get("day", {}).get("c", 0))
        if cp == 0: cp = float(ticker.get("prevDay", {}).get("c", 0))
        return {"current_price": cp}
    except Exception as e:
        logger.error(f"Polygon Error: {e}")
        return {}

def _fetch_alpha_vantage_data(symbol: str) -> dict:
    apikey = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not apikey or "修改成您" in apikey: return {}
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={apikey}"
        res = requests.get(url, timeout=10)
        data = res.json()
        quote = data.get("Global Quote", {})
        if not quote: return {}
        cp = float(quote.get("05. price", 0))
        return {"current_price": cp}
    except Exception as e:
        logger.error(f"AV Error: {e}")
        return {}

def get_stock_data(normalized_symbol: str, market_type: str) -> dict:
    """雙軌交叉比對核心"""
    if market_type == "台股":
        twse = _fetch_twse_data(normalized_symbol)
        fugle = _fetch_fugle_data(normalized_symbol)
        return {"TWSE": twse, "Fugle": fugle}
    else:
        polygon = _fetch_polygon_data(normalized_symbol)
        av = _fetch_alpha_vantage_data(normalized_symbol)
        return {"Polygon": polygon, "Alpha_Vantage": av}

def get_stock_news(original_symbol: str, market_type: str) -> list:
    try:
        if market_type == "台股":
            url = f"https://news.google.com/rss/search?q={original_symbol}+股票&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, features="xml")
            items = soup.findAll('item')
            return [item.title.text for item in items[:3]]
        else:
            ticker = yf.Ticker(original_symbol)
            news = ticker.news
            return [n['title'] for n in news[:3]]
    except Exception as e:
        logger.error(f"Error fetching news for {original_symbol}: {e}")
        return []
