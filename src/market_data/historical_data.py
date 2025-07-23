from datetime import datetime, timedelta

import pandas as pd
import pytz

from src.utils.instruments_util import get_instrument_token
from src.utils.kite_client_util import get_authenticated_kite

IST = pytz.timezone("Asia/Kolkata")

MAX_DAYS_PER_REQUEST = 100
INTERVAL_MAX_DAYS = {
    "minute": 60,
    "3minute": 60,
    "5minute": 60,
    "10minute": 60,
    "15minute": 60,
    "30minute": 60,
    "60minute": 60,
    "day": 3650  # ~10 years
}


def split_date_ranges(start_date, end_date, max_days=MAX_DAYS_PER_REQUEST):
    date_ranges = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").astimezone(IST)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").astimezone(IST)

    while start_dt < end_dt:
        next_dt = min(start_dt + timedelta(days=max_days), end_dt)
        date_ranges.append((start_dt, next_dt))
        start_dt = next_dt + timedelta(seconds=1)
    return date_ranges


def fetch_and_store_historical(trading_symbol, from_date, to_date, interval="5minute"):
    kite = get_authenticated_kite()
    instrument_token = get_instrument_token(trading_symbol)

    max_days = INTERVAL_MAX_DAYS.get(interval, 60)
    date_ranges = split_date_ranges(from_date, to_date, max_days=max_days)

    combined_df = pd.DataFrame()

    print(f"📅 Fetching historical data for '{trading_symbol}' in {len(date_ranges)} parts:")

    for idx, (start, end) in enumerate(date_ranges, 1):
        print(f"🔸 Range {idx}: {start} to {end}")
        historical_data = kite.historical_data(
            instrument_token,
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S"),
            interval
        )
        if historical_data:
            df = pd.DataFrame(historical_data)
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    if not combined_df.empty:
        filename = f"data/historical/{trading_symbol}_{interval}.csv"
        combined_df.to_csv(filename, index=False)
        print(f"📈 Historical data for '{trading_symbol}' saved to {filename}.")
    else:
        print(f"⚠️ No historical data found for '{trading_symbol}'.")
