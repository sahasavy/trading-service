from kiteconnect import KiteConnect

from src.commons.constants.constants import CandleInterval
from src.utils.db_util import get_latest_access_token
import yaml

CONFIG_PATH = "config/config.yaml"
INTERVAL_MAP = {
    "1m": CandleInterval.MIN_1.value,
    "3m": CandleInterval.MIN_3.value,
    "5m": CandleInterval.MIN_5.value,
    "10m": CandleInterval.MIN_10.value,
    "15m": CandleInterval.MIN_15.value,
    "30m": CandleInterval.MIN_30.value,
    "1h": CandleInterval.MIN_60.value,
    "1d": CandleInterval.DAY.value,
}


def read_config():
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)


def get_authenticated_kite():
    config = read_config()
    access_token = get_latest_access_token(config['kite']['api_key'])
    if not access_token:
        raise Exception("No active login. Run login first.")
    kite = KiteConnect(api_key=config['kite']['api_key'])
    kite.set_access_token(access_token)
    return kite


def normalize_interval(custom_interval: str) -> str:
    """
    Converts various custom intervals to KiteConnect-accepted values.
    Raises ValueError for invalid intervals.
    """
    key = custom_interval.strip().lower()
    if key in INTERVAL_MAP:
        return INTERVAL_MAP[key]
    raise ValueError(
        f"Unsupported interval '{custom_interval}'. "
        "Allowed: 1m, 3m, 5m, 10m, 15m, 30m, 1h, 1d"
    )
