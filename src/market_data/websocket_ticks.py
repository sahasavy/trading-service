import json
import os
from datetime import time, datetime

import pytz
import yaml
from kiteconnect import KiteTicker

from src.utils.instruments import get_instrument_token
from src.utils.kite_client import get_authenticated_kite
from src.utils.time_utils import get_current_ist_time

CONFIG_PATH = "config/config.yaml"
DATA_DIR = "data/live_ticks"

IST = pytz.timezone("Asia/Kolkata")

with open(CONFIG_PATH, 'r') as file:
    config = yaml.safe_load(file)


def current_date_str():
    return get_current_ist_time().strftime('%d-%m-%Y')


def get_tokens(symbols):
    return [get_instrument_token(sym.strip()) for sym in symbols]


def create_file_handles(symbols):
    file_handles = {}
    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = current_date_str()
    for sym in symbols:
        filename = f"{DATA_DIR}/{sym}_{date_str}_ticks.jsonl"
        file_handles[sym] = open(filename, "a")
    return file_handles


def start_websocket(symbols):
    tokens = get_tokens(symbols)
    token_symbol_map = dict(zip(tokens, symbols))
    file_handles = create_file_handles(symbols)

    kite = get_authenticated_kite()

    kws = KiteTicker(
        kite.api_key,
        kite.access_token,
        reconnect=config['websocket']['reconnect'],
        reconnect_max_tries=config['websocket']['reconnect_max_tries'],
    )

    def on_ticks(ws, ticks):
        for tick in ticks:
            tick_serialized = {
                k: (v.isoformat() if isinstance(v, (datetime,)) else v)
                for k, v in tick.items()
            }
            symbol = token_symbol_map.get(tick['instrument_token'])
            if symbol:
                json_line = json.dumps(tick_serialized)
                file_handles[symbol].write(json_line + '\n')

    def on_connect(ws, response):
        ws.subscribe(tokens)
        ws.set_mode(ws.MODE_FULL, tokens)
        print(f"🎯 Connected and subscribed: {', '.join(symbols)}")

    def on_close(ws, code, reason):
        print(f"🔴 Websocket closed: {code} - {reason}")
        for fh in file_handles.values():
            fh.close()

    def on_error(ws, error_code, error_message):
        print(f"❌ Error occurred [{error_code}]: {error_message}")

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error

    while True:
        now = get_current_ist_time().time()
        if now >= time(15, 30):
            print("⏰ Market closed, stopping websocket.")
            break
        kws.connect()

    for fh in file_handles.values():
        fh.close()
