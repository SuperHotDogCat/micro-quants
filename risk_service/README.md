# Risk service API
# API
- GET /VaR?symbols={ticker_code}&start={start_date}&end={end_date}
# 実行方法
```
uv run uvicorn main:app --reload --port 8001
```
# Request例
```
curl "http://127.0.0.1:8001/VaR?symbols=SPY&symbols=QQQ&symbols=NVDA&start=2022-05-28&end=2026-05-28"
```