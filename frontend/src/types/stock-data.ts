export interface StockData {
    ticker: string;
    company_name: string;
    currency?: string | null;
    current_price?: number | null;
    sector?: string | null;
    industry?: string | null;
}

export interface HistoricalStockData {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    adjustedClose?: number;
    volume: number;
}