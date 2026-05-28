# Micro Quants Architecture

This project is organized as multiple microservices for quantitative finance systems.

Services are separated by responsibility:

```text
Pricing
Risk
MarketData
Portfolio
Scenario
```

---

# Architecture Overview

```text
                +----------------+
                |  MarketData    |
                +----------------+
                   ↑         ↑
                   |         |
          +--------+         +--------+
          |                           |
+----------------+         +----------------+
|    Pricing     |         |      Risk      |
+----------------+         +----------------+
          ↑                           ↑
          |                           |
          +------------+--------------+
                       |
                +----------------+
                |   Portfolio    |
                +----------------+
                       ↑
                       |
                +----------------+
                |    Scenario    |
                +----------------+
```

---

# Services

---

# MarketData Service

Responsible for market data ingestion and retrieval.

## Responsibilities

* realtime prices
* historical prices
* yield curves
* volatility surfaces
* market snapshots

## Example Endpoints

```http
GET /snapshot
GET /quotes
GET /historical
GET /curve
GET /vol-surface
```

## Example Response

```json
{
  "market_data": {
    "SPY": {
      "historical": [
        {
          "date": "2024-01-01",
          "close": 500.0
        }
      ]
    }
  }
}
```

---

# Pricing Service

Responsible for derivative pricing and sensitivities.

## Responsibilities

* Black-Scholes pricing
* Monte Carlo pricing
* Greeks calculation
* implied volatility

## Example Endpoints

```http
POST /black-scholes
POST /monte-carlo
POST /greeks
```

## Example Request

```json
{
  "spot": 100,
  "strike": 110,
  "rate": 0.03,
  "vol": 0.2,
  "maturity": 1.0
}
```

---

# Risk Service

Responsible for portfolio risk calculations.

## Responsibilities

* Historical VaR
* stress testing
* exposure calculation
* covariance matrix
* returns generation

## Example Endpoints

```http
POST /historical-var
POST /stress-test
POST /exposure
```

## Example Workflow

```text
MarketData
    ↓
returns
    ↓
VaR
```

---

# Portfolio Service

Responsible for portfolio and trade management.

## Responsibilities

* trades
* positions
* portfolio aggregation
* PnL calculation

## Example Endpoints

```http
POST /trades
GET /positions
GET /pnl
```

## Example Position

```json
{
  "symbol": "SPY",
  "quantity": 100
}
```

---

# Scenario Service

Responsible for scenario generation.

## Responsibilities

* parallel yield shifts
* volatility shocks
* spot shocks
* custom scenarios

## Example Endpoints

```http
POST /parallel-shift
POST /vol-shock
POST /spot-shock
```

## Example Scenario

```json
{
  "spot_shift": -0.1
}
```

---

# Service Interaction

## Example Risk Calculation

```text
Portfolio
    ↓
positions

Risk
    ↓
requests market data

MarketData
    ↓
returns prices

Risk
    ↓
computes VaR
```

---

# Why Microservices

Benefits:

* service isolation
* independent scaling
* independent deployment
* clear ownership
* easier experimentation

---

# Suggested Tech Stack

| Service         | Stack            |
| --------------- | ---------------- |
| API             | FastAPI          |
| Data Validation | Pydantic         |
| Market Data     | yfinance         |
| Cache           | Redis            |
| Database        | PostgreSQL       |
| Async Messaging | Kafka / RabbitMQ |
| Container       | Docker           |

---

# Future Improvements

* websocket realtime feed
* async pricing jobs
* GPU Monte Carlo
* distributed risk engine
* portfolio optimization
* volatility calibration
* time-series database
* scenario persistence
* snapshot versioning

# MVP

## MarketData

* historical prices
* multi-symbol snapshot
* adjusted close
* volume
* yfinance integration

---

## Pricing

* Black-Scholes
* Greeks
* simple option pricing API

---

## Risk

* Historical VaR
* exposure
* returns calculation

---

## Portfolio

* trades
* positions
* simple portfolio aggregation

---

## Scenario

* spot shock
* parallel shift
* volatility shock

---

# Tech Stack

* FastAPI
* Pydantic
* yfinance
* uv
* Docker

---

# Future

* realtime feed
* Redis cache
* Monte Carlo
* GPU pricing
* implied vol surface
* yield curve
* persistent database
* async jobs
