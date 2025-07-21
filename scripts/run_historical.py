from src.market_data.historical_data import fetch_and_store_historical
import yaml

CONFIG_PATH = "config/config.yaml"


def read_config():
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)


def normalize_interval(user_interval):
    """
    Converts various user inputs for interval to KiteConnect-accepted values.
    Raises ValueError for invalid intervals.
    """
    valid_intervals = {
        "1m": "minute",
        "3m": "3minute",
        "5m": "5minute",
        "10m": "10minute",
        "15m": "15minute",
        "30m": "30minute",
        "1h": "60minute",
        "1d": "day",
    }

    key = user_interval.strip().lower()
    if key in valid_intervals:
        return valid_intervals[key]
    else:
        raise ValueError(
            f"Unsupported interval '{user_interval}'. "
            "Allowed: 1m, 3m, 5m, 10m, 15m, 30m, 1h, 1d"
        )


if __name__ == "__main__":
    config = read_config()
    trading_symbol = config['historical']['trading_symbol']
    from_date = config['historical']['from_date']
    to_date = config['historical']['to_date']
    interval = normalize_interval(config['historical']['interval'])

    print(f"🚀 trading_symbol: {trading_symbol}")
    print(f"🚀 from_date: {from_date}")
    print(f"🚀 to_date: {to_date}")
    print(f"🚀 interval: {interval}")

    fetch_and_store_historical(
        trading_symbol=trading_symbol,
        from_date=from_date,
        to_date=to_date,
        interval=interval
    )
