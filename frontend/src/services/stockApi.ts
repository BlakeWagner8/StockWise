import type {
    StockData,
    HistoricalStockData
} from "../types/stock-data";

async function getErrorMessage(
    response: Response,
    fallback: string
): Promise<string> {
    try {
        const body: unknown = await response.json();

        if (
            typeof body === "object" &&
            body !== null &&
            "detail" in body
        ) {
            const detail = (body as { detail: unknown }).detail;

            if (typeof detail === "string") {
                return detail;
            }

            if (Array.isArray(detail)) {
                return detail
                    .map((item) => {
                        if (
                            typeof item === "object" &&
                            item !== null
                        ) {
                            const error = item as {
                                loc?: unknown;
                                msg?: unknown;
                            };

                            const message =
                                typeof error.msg === "string"
                                    ? error.msg
                                    : "Invalid value";

                            const location = Array.isArray(error.loc)
                                ? error.loc.slice(1).join(".")
                                : "";

                            return location
                                ? `${location}: ${message}`
                                : message;
                        }

                        return String(item);
                    })
                    .join("; ");
            }
        }
    } catch {
        // Response wasn't valid JSON.
    }

    return fallback;
}

const API_BASE_URL = "http://127.0.0.1:8000";

export async function getStock(
    ticker: string
): Promise<StockData> {

    const response = await fetch(
        `${API_BASE_URL}/stocks/${encodeURIComponent(ticker)}`
    );

    if (!response.ok) {
        throw new Error(
            await getErrorMessage(
                response,
                "Unable to retrieve stock information."
            )
        );
    }

    return response.json();
}

export async function getHistoricalPrices(
    ticker: string,
    period: string = "1y"
): Promise<HistoricalStockData[]> {

    const params = new URLSearchParams({ period });

    const response = await fetch(
        `${API_BASE_URL}/stocks/${encodeURIComponent(ticker)}/history?${params}`
    );

    if (!response.ok) {
        throw new Error(
            await getErrorMessage(
                response,
                "Unable to retrieve historical prices."
            )
        );
    }

    return response.json();
}