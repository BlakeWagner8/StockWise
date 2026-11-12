from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.main import app
from app.models.stock_data import StockData
from app.api.routes import stocks
from app.data_providers.yahoo_finance import MarketDataProviderError

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to StockWise!"
    }


def test_invalid_ticker_format():
    response = client.get("/stocks/MSFT!!!")

    assert response.status_code == 422


def test_stock_endpoint_success(monkeypatch):
    def mock_get_stock_info(ticker):
        return StockData(
            ticker=ticker,
            company_name="Microsoft Corporation",
            currency="USD",
            current_price=500.00,
            sector="Technology",
            industry="Software"
        )

    monkeypatch.setattr(
        stocks,
        "get_stock_info",
        mock_get_stock_info
    )

    response = client.get("/stocks/MSFT")

    assert response.status_code == 200
    assert response.json()["ticker"] == "MSFT"
    assert response.json()["company_name"] == "Microsoft Corporation"


def test_stock_not_found(monkeypatch):
    def mock_get_stock_info(ticker):
        raise ValueError("Stock not found.")

    monkeypatch.setattr(
        stocks,
        "get_stock_info",
        mock_get_stock_info
    )

    response = client.get("/stocks/INVALIDTICKER")

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock not found."


def test_provider_error(monkeypatch):
    def mock_get_stock_info(ticker):
        raise MarketDataProviderError("Provider unavailable.")

    monkeypatch.setattr(
        stocks,
        "get_stock_info",
        mock_get_stock_info
    )

    response = client.get("/stocks/MSFT")

    assert response.status_code == 503


def test_stock_history_success(monkeypatch):
    from datetime import datetime
    from app.models.historical_price_data import HistoricalPriceData

    mock_history = Mock(return_value=[
        HistoricalPriceData(
            date=datetime(2026, 11, 5),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            adjusted_close=103.0,
            volume=1000000
        )
    ])

    monkeypatch.setattr(
        stocks,
        "get_historical_prices",
        mock_history
    )

    response = client.get("/stocks/MSFT/history?period=1y")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["close"] == 103.0
    mock_history.assert_called_once_with(
        "MSFT",
        period="1y",
        start=None,
        end=None
    )


def test_stock_history_with_dates_success(monkeypatch):
    from datetime import datetime
    from unittest.mock import Mock

    from app.models.historical_price_data import HistoricalPriceData

    start = datetime(2026, 11, 4)
    end = datetime(2026, 11, 6)
    get_historical_prices = Mock(return_value=[
        HistoricalPriceData(
            date=datetime(2026, 11, 5),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            adjusted_close=103.0,
            volume=1000000
        )
    ])
    monkeypatch.setattr(stocks, "get_historical_prices", get_historical_prices)

    response = client.get(
        "/stocks/MSFT/history?start=2026-11-04&end=2026-11-06"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["close"] == 103.0
    get_historical_prices.assert_called_once_with(
        "MSFT",
        period=None,
        start=start,
        end=end
    )


def test_stock_history_invalid_date_parameters_return_422():
    invalid_queries = [
        "start=2026-11-04",
        "end=2026-11-06",
        "start=2026-11-06&end=2026-11-04",
        "start=not-a-date&end=2026-11-06",
        "period=1y&start=2026-11-04&end=2026-11-06"
    ]

    for query in invalid_queries:
        response = client.get(f"/stocks/MSFT/history?{query}")
        assert response.status_code == 422, query


def test_stock_history_provider_unavailable(monkeypatch):
    def mock_get_historical_prices(ticker, period="1y", start=None, end=None):
        raise MarketDataProviderError("Provider unavailable.")

    monkeypatch.setattr(
        stocks,
        "get_historical_prices",
        mock_get_historical_prices
    )

    response = client.get("/stocks/MSFT/history?period=1y")

    assert response.status_code == 503