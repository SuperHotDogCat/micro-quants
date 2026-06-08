from fastapi import FastAPI, Query
import numpy as np
import requests
import os

from datetime import datetime

import models


app = FastAPI()

MARKET_HOST = os.environ.get("MARKET_HOST", "127.0.0.1")
MARKET_PORT = os.environ.get("MARKET_PORT", "8000")


# =========================
# Utils
# =========================

def fetch_market_data(
    symbols: list[str],
    start: str,
    end: str,
) -> models.SnapshotResponse:

    params = []

    for symbol in symbols:
        params.append(("symbols", symbol))

    params.append(("start", start))
    params.append(("end", end))

    response = requests.get(
        f"http://{MARKET_HOST}:{MARKET_PORT}/snapshot",
        params=params,
    )

    response.raise_for_status()

    return models.SnapshotResponse(**response.json())


def compute_returns(
    historical: list[models.HistoricalItem],
) -> np.ndarray:

    returns = []

    for i in range(1, len(historical)):

        prev_item = historical[i - 1]
        curr_item = historical[i]

        prev_date = datetime.fromisoformat(prev_item.date)
        curr_date = datetime.fromisoformat(curr_item.date)

        date_diff = (curr_date - prev_date).days

        # =========================
        # Skip if gap > 2 days
        # =========================

        if date_diff > 2:
            continue

        ret = (
            curr_item.close / prev_item.close
        ) - 1.0

        returns.append(ret)

    return np.array(
        returns,
        dtype=np.float64,
    )


def compute_var(
    returns: np.ndarray,
    alpha: float,
) -> float:

    if len(returns) == 0:
        return 0.0

    percentile = (1.0 - alpha) * 100.0

    var = np.percentile(
        returns,
        percentile,
    )

    return float(var)


# =========================
# API
# =========================

@app.get(
    "/VaR",
    response_model=models.VaRResponse,
)
def get_var(
    symbols: list[str] = Query(...),
    start: str = "2024-01-01",
    end: str = "2025-01-01",
    alpha: float = 0.95,
):

    snapshot = fetch_market_data(
        symbols=symbols,
        start=start,
        end=end,
    )

    symbol_to_var: dict[str, float] = {}

    symbol_to_returns: dict[str, list[float]] = {}

    for symbol in symbols:

        historical = snapshot.market_data[symbol].historical

        returns = compute_returns(historical)

        var = compute_var(
            returns=returns,
            alpha=alpha,
        )

        symbol_to_var[symbol] = var

        symbol_to_returns[symbol] = returns.tolist()

    return models.VaRResponse(
        symbols=symbols,
        alpha=alpha,
        start=start,
        end=end,
        symbol_to_var=symbol_to_var,
        symbol_to_returns=symbol_to_returns,
    )
