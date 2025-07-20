import pandas as pd
import os
from src.utils.kite_client import get_authenticated_kite
from src.utils.time_utils import get_current_ist_time

CACHE_FILE = "data/cache/instruments.csv"


def fetch_and_cache_instruments():
    kite = get_authenticated_kite()
    instruments = kite.instruments()
    df = pd.DataFrame(instruments)
    df.to_csv(CACHE_FILE, index=False)
    print(f"✅ Instruments data cached successfully at {get_current_ist_time()}")


def load_instruments_cache():
    if not os.path.exists(CACHE_FILE):
        print("⚠️ Cache not found. Fetching fresh data.")
        fetch_and_cache_instruments()
    return pd.read_csv(CACHE_FILE)


def get_instrument_token(tradingsymbol, exchange="NSE"):
    df = load_instruments_cache()
    result = df[
        (df["tradingsymbol"] == tradingsymbol) &
        (df["exchange"] == exchange)
        ]
    if not result.empty:
        return int(result.iloc[0]["instrument_token"])
    else:
        raise ValueError(f"❌ Instrument '{tradingsymbol}' not found.")
