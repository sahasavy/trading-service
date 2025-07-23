import os
import pandas as pd
import yaml
from src.backtest.engine import run_backtest
from src.backtest.logger import log_run_header
from src.market_data.historical_data import fetch_and_store_historical

CONFIG_PATH = "config/config.yaml"


def normalize_interval(interval):
    m = interval.strip().lower()
    mp = {
        "1m": "minute",
        "3m": "3minute",
        "5m": "5minute",
        "10m": "10minute",
        "15m": "15minute",
        "30m": "30minute",
        "1h": "60minute",
        "1d": "day"
    }
    return mp[m]


def load_or_fetch_data(trading_symbol, interval_key, from_date, to_date):
    filename = f"data/historical/{trading_symbol}_{interval_key}.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename, parse_dates=['date'])
        print(f"✅ Loaded data for {trading_symbol} {interval_key} from {filename}")
        return df
    else:
        print(f"⬇️  Data for {trading_symbol} {interval_key} not found, fetching...")
        fetch_and_store_historical(trading_symbol, from_date, to_date, interval_key)
        if os.path.exists(filename):
            df = pd.read_csv(filename, parse_dates=['date'])
            return df
        else:
            print(f"❌ Failed to fetch data for {trading_symbol} {interval_key}")
            return pd.DataFrame()


def main():
    config = yaml.safe_load(open(CONFIG_PATH))

    backtest_cfg = config['backtest']
    trading_symbols = backtest_cfg['trading_symbols']
    intervals = backtest_cfg['intervals']
    from_date = backtest_cfg['from_date']
    to_date = backtest_cfg['to_date']
    train_split = backtest_cfg.get('train_split', 1.0)
    initial_capital = backtest_cfg.get('initial_capital', 1000000)
    stop_loss_pct = backtest_cfg.get('stop_loss_pct', 0.02)
    trailing_stop_loss_pct = backtest_cfg.get('trailing_stop_loss_pct', 0.02)
    target_profit_pct = backtest_cfg.get('target_profit_pct', 0.04)
    hold_min_bars = backtest_cfg.get('hold_min_bars', 2)
    hold_max_bars = backtest_cfg.get('hold_max_bars', 120)
    contract_size = backtest_cfg.get('contract_size', 1)
    fill_rate = backtest_cfg.get('fill_rate', 1.0)
    slippage_pct = backtest_cfg.get('slippage_pct', 0.001)
    intraday_only = backtest_cfg.get('intraday_only', True)

    brokerage_cfg = config['brokerage']
    segment = brokerage_cfg.get('segment')
    exchange = brokerage_cfg.get('exchange')

    strategy_cfg = config['strategy']
    strategy_name = strategy_cfg['name']
    fast_list = strategy_cfg['ema_fast_list']
    slow_list = strategy_cfg['ema_slow_list']

    summary_metrics = []
    for trading_symbol in trading_symbols:
        for interval in intervals:
            interval_key = normalize_interval(interval)
            df = load_or_fetch_data(trading_symbol, interval_key, from_date, to_date)

            if df.empty:
                continue

            df.sort_values('date', inplace=True)
            df.reset_index(drop=True, inplace=True)

            for fast in fast_list:
                for slow in slow_list:
                    if fast >= slow:
                        continue

                    log_run_header(trading_symbol, interval, fast, slow)

                    _, metrics = run_backtest(
                        df,
                        strategy_name,
                        fast, slow,
                        initial_capital,
                        stop_loss_pct,
                        trailing_stop_loss_pct,
                        target_profit_pct,
                        contract_size,
                        hold_min_bars,
                        hold_max_bars,
                        fill_rate,
                        slippage_pct,
                        segment,
                        exchange,
                        train_split,
                        intraday_only,
                        verbose=True,
                        save_results=True,
                        token=trading_symbol,
                        interval=interval_key,
                    )

                    # Save summary metrics for all splits (all/train/test)
                    for metric in metrics:
                        metric.update(dict(token=trading_symbol, interval=interval_key, fast=fast, slow=slow))
                        summary_metrics.append(metric)

    # Save all metrics summary
    if summary_metrics:
        pd.DataFrame(summary_metrics).to_csv("data/results/metrics_summary.csv", index=False)
        print("✅ All metrics summary saved to data/results/metrics_summary.csv")


if __name__ == "__main__":
    main()
