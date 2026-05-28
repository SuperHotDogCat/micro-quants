# Market service API

## GET /snapshot

Fetch historical market data for one or more ticker symbols.

# Run Server

```bash
uv run uvicorn main:app --reload
```
---

# Query Parameters

| parameter | type | required | description |
|---|---|---|---|
| symbols | list[str] | yes | ticker symbols |
| start | str | no | start date |
| end | str | no | end date |

---

# Example Request

```http
GET /snapshot?symbols=SPY&symbols=QQQ&symbols=VT
```

Fetch historical market data for:

- SPY
- QQQ
- NVDA

using the default date range.

---

# Example Request with Date Range

```http
GET /snapshot?symbols=SPY&symbols=QQQ&start=2024-01-01&end=2025-01-01
```

Fetch data between:

```text
2024-01-01 → 2025-01-01
```

for:

- SPY
- QQQ

---

# Example Using curl

```bash
curl "http://127.0.0.1:8000/snapshot?symbols=SPY&symbols=QQQ&symbols=NVDA"
```

---

# Example Response

```json
{
  "symbols": [
    "SPY",
    "QQQ",
    "NVDA"
  ],
  "start": "2024-01-01",
  "end": "2025-01-01",
  "market_data": {
    "SPY": {
      "historical": [
        {
          "date": "2024-01-02 00:00:00",
          "close": 459.99,
          "volume": 123623700
        }
        ...
      ]
    }
    ...
  }
}
```

---

# Response Structure

```text
market_data
    └ symbol
        └ historical
            └ date
            └ close
            └ volume
```

Example:

```text
market_data["SPY"]["historical"][0]["close"]
```

returns the close price of SPY for the first historical entry.

---

# Important

## Correct Multi-Symbol Format

Use:

```http
?symbols=SPY&symbols=QQQ&symbols=NVDA
```

NOT:

```http
?symbols=SPY,QQQ,NVDA
```

because FastAPI parses repeated query parameters into `list[str]`.
