from pydantic import BaseModel

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

class PortfolioPoint(BaseModel):
    mean: float
    vol: float
    weights: dict[str, float]


class PortfolioResponse(BaseModel):
    symbols: list[str]
    start: str
    end: str

    best_sharpe_ratio_portfolio: PortfolioPoint

    min_var_portfolio: PortfolioPoint

    portfolio_points: list[PortfolioPoint]
