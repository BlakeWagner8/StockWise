from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HistoricalPriceData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    date: datetime
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None = None
    volume: int