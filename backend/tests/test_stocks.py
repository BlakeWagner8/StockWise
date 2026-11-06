from fastapi.testclient import TestClient

from app.main import app
from app.models.stock_data import StockData
from app.api.routes import stocks

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
        raise RuntimeError("Provider unavailable.")

    monkeypatch.setattr(
        stocks,
        "get_stock_info",
        mock_get_stock_info
    )

    response = client.get("/stocks/MSFT")

    assert response.status_code == 502