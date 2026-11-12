import math
from datetime import datetime

from app.models.historical_price_data import HistoricalPriceData
from app.models.stock_data import StockData
from app.data_providers import yahoo_finance as yf

##general service for retrieving current stock information based on ticker symbol
def get_stock_info(ticker: str) -> StockData:
    info = yf.get_ticker_info(ticker)

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


# get historical prices for a specified ticker
def get_historical_prices(
    ticker: str,
    period: str = "1y",
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[HistoricalPriceData]:

    history = yf.get_ticker_history(
        ticker,
        period=period,
        start=start,
        end=end
    )

    if history.empty:
        raise ValueError("No historical price data available.")

    prices = []

    for date, row in history.iterrows():
        adjusted_close = row.get("Adj Close")

        if adjusted_close is not None and math.isnan(float(adjusted_close)):
            adjusted_close = None

        prices.append(
            HistoricalPriceData(
                date=date,
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                adjusted_close=adjusted_close,
                volume=int(row["Volume"])
            )
        )

    return prices