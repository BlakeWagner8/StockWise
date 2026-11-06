import yfinance as yf

from app.models.stock_data import StockData

##general endpoint for retireving generic stock information based on ticker symbol
def get_stock_info(ticker: str) -> StockData:
    stock = yf.Ticker(ticker)
    info = stock.info
    company_name = info.get("longName")

    if not company_name:
        raise ValueError("Stock not found or company information unavailable.")

    return StockData(
        ticker=ticker.upper(),
        company_name=company_name,
        currency=info.get("currency"),
        current_price=info.get("currentPrice"),
        sector=info.get("sector"),
        industry=info.get("industry"),
        market_cap=info.get("marketCap"),
        pe_ratio=info.get("trailingPE"),
        dividend_yield= info.get("dividendYield"),
    )