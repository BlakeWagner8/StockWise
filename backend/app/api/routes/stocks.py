from fastapi import APIRouter, HTTPException, Path, Query
from app.models.historical_price_data import HistoricalPriceData
from app.models.stock_data import StockData
from app.services.stock_service import get_stock_info, get_historical_prices
from app.data_providers.yahoo_finance import MarketDataProviderError
from datetime import datetime

router = APIRouter()

@router.get("/{ticker}", response_model=StockData)
def read_stock(
    ticker: str = Path(
        min_length=1,
        max_length=15,
        pattern=r"^[A-Za-z0-9.^=-]+$",
    )
):
    try: return get_stock_info(ticker.upper())

    except ValueError as e:
        raise HTTPException(
            status_code=404, 
            detail=str(e)
        )
    except MarketDataProviderError as e:
        raise HTTPException(
            status_code=503,
            detail="The market data provider is unavailable."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred while fetching stock information: {str(e)}"
        )

    
@router.get(
    "/{ticker}/history",
    response_model=list[HistoricalPriceData]
)
def read_stock_history(
    ticker: str = Path(
        min_length=1,
        max_length=15,
        pattern=r"^[A-Za-z0-9.^=-]+$"
    ),
    period: str | None = Query(
        default=None,
        pattern=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$"
    ),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None)
):
    if (start is None) != (end is None):
        raise HTTPException(
            status_code=422,
            detail="Both start and end dates must be provided."
        )

    if start is not None and end is not None:
        if start >= end:
            raise HTTPException(
                status_code=422,
                detail="Start date must be before end date."
            )

        if period is not None:
            raise HTTPException(
                status_code=422,
                detail="Period cannot be combined with start and end dates."
            )

        period = None
    else:
        period = period or "1y"

    try:
        return get_historical_prices(
            ticker.upper(),
            period=period,
            start=start,
            end=end
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except MarketDataProviderError as e:
        raise HTTPException(
            status_code=503,
            detail="The market data provider is unavailable."
        )
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching historical stock data: {str(e)}"
        )