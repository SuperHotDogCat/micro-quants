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

class VaRResponse(BaseModel):
    symbols: list[str]
    alpha: float
    start: str
    end: str
    symbol_to_var: dict[str, float] # symbol -> var
    symbol_to_returns: dict[str, list[float]] # symbol -> return
