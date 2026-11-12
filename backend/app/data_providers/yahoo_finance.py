import yfinance as yf
from datetime import datetime


class MarketDataProviderError(Exception):
    """Raised when an external market data provider fails."""

def get_ticker_info(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        return stock.info

    except Exception as e:
        raise MarketDataProviderError(
            "Unable to retrieve company information."
        ) from e


def get_ticker_history(
    ticker: str,
    period: str | None = "1y",
    start: datetime | None = None,
    end: datetime | None = None,
    interval: str = "1d"
):
    try:
        stock = yf.Ticker(ticker)

        if start is not None and end is not None:
            return stock.history(
                start=start,
                end=end,
                interval=interval,
                auto_adjust=False
            )

        return stock.history(
            period=period,
            interval=interval,
            auto_adjust=False
        )

    except Exception as e:
        raise MarketDataProviderError(
            "Unable to retrieve historical stock data."
        ) from e