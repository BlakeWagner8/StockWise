from pydantic import BaseModel, ConfigDict

##Stock data model for generic stock data
class StockData(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    ticker: str
    company_name: str
    currency: str | None = None
    current_price: float | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
