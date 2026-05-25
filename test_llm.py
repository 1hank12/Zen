import asyncio
from ai.llm import resolve_stock_symbol
from dotenv import load_dotenv

async def main():
    load_dotenv()
    res = await resolve_stock_symbol("2330")
    print(f"2330 resolved to: {res}")
    res2 = await resolve_stock_symbol("0050")
    print(f"0050 resolved to: {res2}")

asyncio.run(main())
