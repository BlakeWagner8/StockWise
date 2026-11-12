from datetime import datetime
from unittest.mock import Mock

import pandas as pd
import pytest

from app.data_providers import yahoo_finance
from app.data_providers.yahoo_finance import MarketDataProviderError
from app.models.stock_data import StockData
from app.services import stock_service


class MockTicker:
    info = {
        "longName": "Microsoft Corporation",
        "currency": "USD",
        "currentPrice": 500.0,
        "sector": "Technology",
        "industry": "Software"
    }


def test_get_stock_info(monkeypatch):
    monkeypatch.setattr(
        stock_service.yf,
        "get_ticker_info",
        lambda ticker: MockTicker.info
    )

    result = stock_service.get_stock_info("MSFT")

    assert isinstance(result, StockData)
    assert result.ticker == "MSFT"
    assert result.company_name == "Microsoft Corporation"
    assert result.currency == "USD"
    assert result.current_price == 500.0
    assert result.sector == "Technology"
    assert result.industry == "Software"


def test_get_stock_info_missing_company_name_raises_value_error(monkeypatch):
    monkeypatch.setattr(
        stock_service.yf,
        "get_ticker_info",
        lambda ticker: {}
    )

    with pytest.raises(ValueError, match="Stock not found"):
        stock_service.get_stock_info("MSFT")


def test_get_historical_prices(monkeypatch):
    start = datetime(2026, 11, 4)
    end = datetime(2026, 11, 6)
    mock_history = pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 101.0],
            "Close": [103.0, 104.0],
            "Adj Close": [103.0, 104.0],
            "Volume": [1000000, 1200000]
        },
        index=pd.to_datetime([
            "2026-11-04",
            "2026-11-05"
        ])
    )

    get_ticker_history = Mock(return_value=mock_history)
    monkeypatch.setattr(
        yahoo_finance,
        "get_ticker_history",
        get_ticker_history
    )

    result = stock_service.get_historical_prices(
        "MSFT",
        period=None,
        start=start,
        end=end
    )

    get_ticker_history.assert_called_once_with(
        "MSFT",
        period=None,
        start=start,
        end=end
    )
    assert len(result) == 2
    assert result[0].close == 103.0
    assert result[1].volume == 1200000


@pytest.mark.parametrize(
    "provider_call",
    [yahoo_finance.get_ticker_info, yahoo_finance.get_ticker_history]
)
def test_market_data_provider_wraps_provider_exception(
    monkeypatch,
    provider_call
):
    def raise_provider_error(ticker):
        raise RuntimeError("Yahoo Finance unavailable.")

    monkeypatch.setattr(
        yahoo_finance.yf,
        "Ticker",
        raise_provider_error
    )

    with pytest.raises(MarketDataProviderError):
        provider_call("MSFT")