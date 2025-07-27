import json
import os
import threading
from datetime import time, datetime

from kiteconnect import KiteTicker

from src.utils.file_util import read_config
from src.utils.instruments_util import get_instrument_token
from src.utils.kite_client_util import get_authenticated_kite
from src.utils.time_util import get_current_ist_time, current_date_str

CONFIG_PATH = "config/config.yaml"
TICK_DATA_DIR = "data/live_ticks"


def get_tokens(symbols):
    return [get_instrument_token(symbol.strip()) for symbol in symbols]


def create_file_handles(symbols):
    file_handles = {}
    os.makedirs(TICK_DATA_DIR, exist_ok=True)
    date_str = current_date_str()
    for symbol in symbols:
        symbol_dir = os.path.join(TICK_DATA_DIR, symbol)
        os.makedirs(symbol_dir, exist_ok=True)
        filename = f"{symbol_dir}/{symbol}_{date_str}_ticks.jsonl"
        file_handles[symbol] = open(filename, "a")
    return file_handles


def start_websocket(symbols):
    config = read_config(CONFIG_PATH)

    tokens = get_tokens(symbols)
    token_symbol_map = dict(zip(tokens, symbols))
    file_handles = create_file_handles(symbols)

    kite = get_authenticated_kite()
    is_closed = {"status": False}

    kws = KiteTicker(
        kite.api_key,
        kite.access_token,
        reconnect=config['websocket']['reconnect'],
        reconnect_max_tries=config['websocket']['reconnect_max_tries'],
    )

    now = get_current_ist_time()
    market_close = now.replace(
        hour=config['websocket']['market_close_hour'],
        minute=config['websocket']['market_close_minute'],
        second=0,
        microsecond=0
    )
    if now > market_close:
        print("⏰ Market already closed, skipping websocket connection.")
        for fh in file_handles.values():
            if not fh.closed:
                fh.close()
        return

    def on_ticks(ws, ticks):
        if is_closed["status"]:
            return
        now_time = get_current_ist_time().time()
        if now_time >= time(config['websocket']['market_close_hour'], config['websocket']['market_close_minute']):
            print("⏰ Market closed! Closing websocket and files.")
            ws.close()
            is_closed["status"] = True
            return
        for tick in ticks:
            tick_serialized = {
                k: (v.isoformat() if isinstance(v, (datetime,)) else v)
                for k, v in tick.items()
            }
            symbol = token_symbol_map.get(tick['instrument_token'])
            if symbol:
                fh = file_handles[symbol]
                if not fh.closed:
                    json_line = json.dumps(tick_serialized)
                    fh.write(json_line + '\n')

    def on_connect(ws, response):
        ws.subscribe(tokens)
        ws.set_mode(ws.MODE_FULL, tokens)
        print(f"🎯 Connected and subscribed: {', '.join(symbols)}")

    def on_close(ws, code, reason):
        print(f"🔴 Websocket closed: {code} - {reason}")
        if not is_closed["status"]:
            is_closed["status"] = True
            for fh in file_handles.values():
                if not fh.closed:
                    fh.close()

    def on_error(ws, error_code, error_message):
        print(f"❌ Error occurred [{error_code}]: {error_message}")
        if not is_closed["status"]:
            is_closed["status"] = True
            for fh in file_handles.values():
                if not fh.closed:
                    fh.close()

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error

    def schedule_close_ws():
        wait_sec = (market_close - now).total_seconds()
        threading.Timer(wait_sec, lambda: kws.close()).start()
        print(f"🕒 Websocket will be auto-closed at {market_close.time()} IST (in {wait_sec / 60:.1f} min)")

    schedule_close_ws()
    kws.connect()
