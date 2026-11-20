import { useState } from "react";
import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from "recharts";

import {
    getStock,
    getHistoricalPrices
} from "../services/stockApi";

import type {
    StockData,
    HistoricalPriceData
} from "../types/stock";

const periods = ["1mo", "3mo", "6mo", "1y", "5y"];

function AnalyzeStock() {
    const [ticker, setTicker] = useState("");
    const [stock, setStock] = useState<StockData | null>(null);
    const [historicalPrices, setHistoricalPrices] =
        useState<HistoricalPriceData[]>([]);

    const [period, setPeriod] = useState("1y");

    const [loading, setLoading] = useState(false);
    const [historyLoading, setHistoryLoading] = useState(false);

    const [error, setError] = useState<string | null>(null);
    const [historyError, setHistoryError] =
        useState<string | null>(null);

    async function loadHistoricalPrices(
        stockTicker: string,
        selectedPeriod: string
    ) {
        setHistoryLoading(true);
        setHistoryError(null);

        try {
            const result = await getHistoricalPrices(
                stockTicker,
                selectedPeriod
            );

            setHistoricalPrices(result);
        } catch (err) {
            setHistoricalPrices([]);

            setHistoryError(
                err instanceof Error
                    ? err.message
                    : "Unable to retrieve historical prices."
            );
        } finally {
            setHistoryLoading(false);
        }
    }

    async function handleSearch() {
        const normalizedTicker = ticker.trim().toUpperCase();

        if (!normalizedTicker) {
            setError("Please enter a stock ticker.");
            return;
        }

        if (!/^[A-Z0-9.^=-]{1,15}$/.test(normalizedTicker)) {
            setError("Please enter a valid stock ticker.");
            return;
        }

        setLoading(true);
        setError(null);
        setStock(null);
        setHistoricalPrices([]);
        setHistoryError(null);

        try {
            const result = await getStock(normalizedTicker);

            setStock(result);
            setTicker(normalizedTicker);

            await loadHistoricalPrices(
                normalizedTicker,
                period
            );
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "An unexpected error occurred."
            );
        } finally {
            setLoading(false);
        }
    }

    async function handlePeriodChange(
        selectedPeriod: string
    ) {
        setPeriod(selectedPeriod);

        if (stock) {
            await loadHistoricalPrices(
                stock.ticker,
                selectedPeriod
            );
        }
    }

    return (
        <main>
            <h1>Analyze a Stock</h1>

            <div>
                <input
                    type="text"
                    placeholder="Enter a ticker (e.g. MSFT)"
                    value={ticker}
                    onChange={(e) =>
                        setTicker(e.target.value.toUpperCase())
                    }
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            void handleSearch();
                        }
                    }}
                />

                <button
                    onClick={handleSearch}
                    disabled={loading}
                >
                    {loading ? "Searching..." : "Search"}
                </button>
            </div>

            {error && <p role="alert">{error}</p>}

            {stock && (
                <section>
                    <h2>{stock.company_name}</h2>

                    <p>Ticker: {stock.ticker}</p>

                    <p>
                        Current Price:{" "}
                        {stock.current_price ?? "Unavailable"}
                    </p>

                    <p>
                        Currency: {stock.currency ?? "Unavailable"}
                    </p>

                    <p>
                        Sector: {stock.sector ?? "Unavailable"}
                    </p>

                    <p>
                        Industry: {stock.industry ?? "Unavailable"}
                    </p>

                    <hr />

                    <h2>Historical Prices</h2>

                    <div>
                        {periods.map((option) => (
                            <button
                                key={option}
                                onClick={() =>
                                    void handlePeriodChange(option)
                                }
                                disabled={historyLoading}
                                aria-pressed={period === option}
                            >
                                {option}
                            </button>
                        ))}
                    </div>

                    {historyLoading && (
                        <p>Loading historical prices...</p>
                    )}

                    {historyError && (
                        <p role="alert">{historyError}</p>
                    )}

                    {!historyLoading &&
                        !historyError &&
                        historicalPrices.length > 0 && (
                            <div style={{ width: "100%", height: 350 }}>
                                <ResponsiveContainer>
                                    <LineChart
                                        data={historicalPrices}
                                        margin={{
                                            top: 10,
                                            right: 20,
                                            left: 10,
                                            bottom: 10
                                        }}
                                    >
                                        <CartesianGrid strokeDasharray="3 3" />

                                        <XAxis
                                            dataKey="date"
                                            tickFormatter={(value) =>
                                                new Date(value).toLocaleDateString()
                                            }
                                        />

                                        <YAxis
                                            domain={["auto", "auto"]}
                                        />

                                        <Tooltip
                                            labelFormatter={(value) =>
                                                new Date(value).toLocaleDateString()
                                            }
                                        />

                                        <Line
                                            type="monotone"
                                            dataKey="close"
                                            stroke="#2563eb"
                                            dot={false}
                                            name="Closing Price"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        )}

                    {!historyLoading &&
                        !historyError &&
                        historicalPrices.length === 0 && (
                            <p>No historical price data available.</p>
                        )}
                </section>
            )}
        </main>
    );
}

export default AnalyzeStock;