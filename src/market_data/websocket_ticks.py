import pandas as pd
from kiteconnect import KiteTicker
from src.utils.kite_client import get_authenticated_kite
from src.utils.instruments import get_instrument_token

TRADING_SYMBOLS = ["HDFCBANK", "RELIANCE"]


def on_ticks(ws, ticks):
    df = pd.DataFrame(ticks)
    df.to_csv("data/live_ticks/ticks.csv", mode='a', header=False, index=False)
    print(f"✅ Received ticks: {len(ticks)}")
    # instrument_token = 256265
    # timestamp = get_current_ist_time().strftime("%Y%m%d_%H%M%S")
    # filename = f"data/live_ticks/ticks_{instrument_token}_{timestamp}.csv"
    # df.to_csv(filename, mode='a', header=False, index=False)
    # print("✅ Tick data appended.")


def on_connect(ws, response):
    tokens = [get_instrument_token(symbol) for symbol in TRADING_SYMBOLS]
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL, tokens)
    print(f"🎯 Subscribed to ticks for: {', '.join(TRADING_SYMBOLS)}")


def connect_websocket():
    kite = get_authenticated_kite()
    kws = KiteTicker(kite.api_key, kite.access_token)
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.connect()
