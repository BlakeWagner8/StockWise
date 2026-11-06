from fastapi import APIRouter, HTTPException, Path
from app.models.stock_data import StockData
from app.services.stock_service import get_stock_info

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
    except Exception as e:
        raise HTTPException(
            status_code=502, 
            detail=f"An error occurred while fetching stock information: {str(e)}"
        )