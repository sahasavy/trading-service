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

python3 -m scripts.run_historical
```

### 📈 Live Websocket (For Fetching live tick data)

```bash

python3 -m scripts.run_websocket
```

## ⚠️ Notes:

- Generate Zerodha tokens daily after 7 AM IST.
- All timestamps are explicitly stored and processed in **Indian Standard Time (IST, UTC+5:30)** to match Zerodha API's
  data timezone standards.

## 📚 Instruments Data Caching:

- Instruments cached at `data/cache/instruments.csv`.
- Weekly cache refresh using APScheduler:

```bash

python3 -m scripts.run_cache_scheduler
```
