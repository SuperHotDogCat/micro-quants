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

@app.get(
    "/portfolio-curve",
    response_model=models.PortfolioResponse
)
def get_portfolio_curve(
    symbols: list[str] = Query(...),
    start: str = "2024-01-01",
    end: str = "2025-01-01",
):

    snapshot = fetch_market_data(
        symbols=symbols,
        start=start,
        end=end,
    )

    # =========================================================
    # Build returns matrix
    # shape = [T, N]
    # =========================================================

    returns_list = []

    for symbol in symbols:

        historical = snapshot.market_data[symbol].historical

        returns = compute_returns(historical)

        returns_list.append(returns)

    # transpose
    # [N, T] -> [T, N]

    returns_matrix = np.array(returns_list).T

    # =========================================================
    # Statistics
    # =========================================================

    mean_returns = np.mean(
        returns_matrix,
        axis=0,
    )

    cov_matrix = np.cov(
        returns_matrix.T,
    )

    n_assets = len(symbols)

    # =========================================================
    # Monte Carlo portfolios
    # =========================================================

    n_portfolios = 1000

    portfolio_points: list[tuple[float, float]] = []

    best_sharpe_ratio = -1e18
    best_sharpe_ratio_point = (0.0, 0.0)

    min_var = 1e18
    min_var_point = (0.0, 0.0)

    for _ in range(n_portfolios):

        # =====================================================
        # Random weights
        # =====================================================

        weights = np.random.random(n_assets)

        weights /= np.sum(weights)

        # =====================================================
        # Portfolio mean
        # =====================================================

        portfolio_mean = float(
            weights @ mean_returns
        )

        # =====================================================
        # Portfolio variance
        # =====================================================

        portfolio_var = float(
            weights @ cov_matrix @ weights
        )

        # =====================================================
        # Sharpe ratio
        # rf = 0 for MVP
        # =====================================================

        portfolio_vol = np.sqrt(portfolio_var)

        sharpe_ratio = portfolio_mean / portfolio_vol

        # =====================================================
        # Save point
        # =====================================================
        portfolio_point = models.PortfolioPoint(
            mean=portfolio_mean,
            vol=portfolio_vol,
            weights={
                symbol: float(weight)
                for symbol, weight in zip(symbols, weights)
            }
        )

        portfolio_points.append(portfolio_point)

        # =====================================================
        # Best Sharpe
        # =====================================================

        if sharpe_ratio > best_sharpe_ratio:

            best_sharpe_ratio = sharpe_ratio

            best_sharpe_ratio_portfolio = portfolio_point

        # =====================================================
        # Min variance
        # =====================================================

        if portfolio_var < min_var:

            min_var = portfolio_var

            min_var_portfolio = portfolio_point

    return models.PortfolioResponse(
        symbols=symbols,
        start=start,
        end=end,

        best_sharpe_ratio_portfolio=
            best_sharpe_ratio_portfolio,

        min_var_portfolio=
            min_var_portfolio,

        portfolio_points=portfolio_points,
    )
