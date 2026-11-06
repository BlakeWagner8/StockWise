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
        "Ticker",
        lambda ticker: MockTicker()
    )

    result = stock_service.get_stock_info("MSFT")

    assert isinstance(result, StockData)
    assert result.ticker == "MSFT"
    assert result.company_name == "Microsoft Corporation"
    assert result.currency == "USD"
    assert result.current_price == 500.0
    assert result.sector == "Technology"
    assert result.industry == "Software"