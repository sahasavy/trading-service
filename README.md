# trading-service

Automated algorithmic trading using Zerodha Kite Connect sdk

## Installation steps

```bash

python3 -m venv venv
source venv/bin/activate            # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running scripts (always run inside virtual env (venv))

### 🔐 Authentication (Interactive, For Zerodha login)

```bash

python3 -m scripts.run_login
```

### 📈 Historical Data (For Fetching historic data per token)

```bash

python3 -m scripts.run_historical_data
```

### 📈 Indicator Features (For adding indicator feature values to historic data candles)

```bash

python3 -m scripts.run_feature_enrichment
```

### 📈 Live Websocket (For Fetching live tick data)

```bash

python3 -m scripts.run_websocket            # OR, for scheduler: python3 -m scripts.scheduler.run_websocket_scheduler
```

### 📈 Backtest (Includes grid-search)

```bash

python3 -m scripts.run_backtest
```

## Schedulers:

### 📚 Instruments Data Caching:

- Instruments cached at `data/cache/instruments.csv`.
- Weekly cache refresh using APScheduler:

```bash

python3 -m scripts.scheduler.run_cache_scheduler
```

### 📚 Websocket:

```bash

python3 -m scripts.scheduler.run_websocket_scheduler
```

## ⚠️ Notes:

- Generate Zerodha tokens daily after 7 AM IST.
- All timestamps are explicitly stored and processed in **Indian Standard Time (IST, UTC+5:30)** to match Zerodha API's
  data timezone standards.
