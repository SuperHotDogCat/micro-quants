import time
from fastapi import FastAPI, Query
from pydantic import BaseModel
import yfinance as yf

app = FastAPI()
cache = {} # (symbols, start, end)がkey
CACHE_TTL = 3 # TTL

class HistoricalItem(BaseModel):
    date: str
    close: float
    volume: int

class MarketData(BaseModel):
    historical: list[HistoricalItem]

class SnapshotResponse(BaseModel):
    symbols: list[str]
    start: str
    end: str
    market_data: dict[str, MarketData]

def fetch_market_data(
    symbols: list[str],
    start: str,
    end: str,
) -> dict[str, MarketData]:

    df = yf.download(
        tickers=symbols,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=True, # splitなどの影響を考えて調整する
        group_by="column",
        threads=True,
    )

    result: dict[str, MarketData] = {}

    for symbol in symbols:

        historical: list[HistoricalItem] = []
        close_series = df["Close"][symbol].dropna()
        volume_series = df["Volume"][symbol].dropna()

        for idx in close_series.index:

            close = float(close_series.loc[idx])

            volume = int(volume_series.loc[idx])

            historical.append(
                HistoricalItem(
                    date=str(idx),
                    close=close,
                    volume=volume,
                )
            )

        result[symbol] = MarketData(
            historical=historical
        )

    return result

@app.get(
    "/snapshot",
    response_model=SnapshotResponse,
)
def snapshot(
    symbols: list[str] = Query(...),
    start: str = "2024-01-01",
    end: str = "2025-01-01",
):
    # cache key 
    cache_key = ( tuple(sorted(symbols)), start, end, )
    now = time.time()

    if cache_key in cache: 
        cached = cache[cache_key] 
        age = now - cached["timestamp"]
        if age < CACHE_TTL:
            return cached["data"]
        else:
            del cache[cache_key]

    market_data = fetch_market_data(
        symbols=symbols,
        start=start,
        end=end,
    )

    response = SnapshotResponse(
        symbols=symbols,
        start=start,
        end=end,
        market_data=market_data,
    )
    # cache
    cache[cache_key] = { "timestamp": now, "data": response}

    return response
