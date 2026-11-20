from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import stocks

app = FastAPI(title="StockWise API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to StockWise!"}

app.include_router(
    stocks.router,
    prefix="/stocks",
    tags=["stocks"]
)