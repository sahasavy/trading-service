from src.market_data.historical_data import fetch_and_store_historical

from src.utils.file_util import read_config
from src.utils.kite_client_util import normalize_interval

CONFIG_PATH = "config/config.yaml"


if __name__ == "__main__":
    config = read_config(CONFIG_PATH)

    historical_cfg = config['historical']
    trading_symbols = historical_cfg['trading_symbols']
    intervals = historical_cfg['intervals']
    from_date = historical_cfg['from_date']
    to_date = historical_cfg['to_date']

    for trading_symbol in trading_symbols:
        for interval in intervals:
            interval = normalize_interval(interval)
            fetch_and_store_historical(
                trading_symbol=trading_symbol,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
