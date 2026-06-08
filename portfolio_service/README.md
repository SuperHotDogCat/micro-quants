uv run uvicorn main:app --reload --port 8002
curl "http://127.0.0.1:8002/portfolio-curve?symbols=SPY&symbols=QQQ&symbols=NVDA"
