from fastapi import FastAPI, HTTPException

from app.api.routes import stocks

app = FastAPI(title="StockWise API")

@app.get("/")
def home():
    return {"message": "Welcome to StockWise!"}

app.include_router(
    stocks.router,
    prefix="/stocks",
    tags=["stocks"]
)