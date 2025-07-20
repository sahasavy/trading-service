from src.market_data.historical_data import fetch_and_store_historical

if __name__ == "__main__":
    trading_symbol = "HDFCBANK"
    from_date = "2025-01-01 09:15:00"
    to_date = "2025-07-19 15:30:00"
    interval = "5minute"

    fetch_and_store_historical(
        trading_symbol=trading_symbol,
        from_date=from_date,
        to_date=to_date,
        interval=interval
    )
