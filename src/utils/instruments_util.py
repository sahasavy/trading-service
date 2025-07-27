import pandas as pd
import os

from src.commons.constants.constants import Exchange
from src.utils.kite_client_util import get_authenticated_kite
from src.utils.time_util import get_current_ist_time

CACHE_DATA_DIR = "data/cache"
CACHE_FILE = f"{CACHE_DATA_DIR}/instruments.csv"


def fetch_and_cache_instruments():
    kite = get_authenticated_kite()
    instruments = kite.instruments()
    df = pd.DataFrame(instruments)

    os.makedirs(CACHE_DATA_DIR, exist_ok=True)
    df.to_csv(CACHE_FILE, index=False)
    print(f"✅ Instruments data cached successfully at {get_current_ist_time()}")


def load_instruments_cache():
    if not os.path.exists(CACHE_FILE):
        print("⚠️ Cache not found. Fetching fresh data.")
        fetch_and_cache_instruments()
    return pd.read_csv(CACHE_FILE)


def get_instrument_token(trading_symbol, exchange=Exchange.NSE.name):
    df = load_instruments_cache()
    result = df[
        (df["tradingsymbol"] == trading_symbol) &
        (df["exchange"] == exchange)
        ]
    if not result.empty:
        return int(result.iloc[0]["instrument_token"])
    else:
        raise ValueError(f"❌ Instrument '{trading_symbol}' not found.")
