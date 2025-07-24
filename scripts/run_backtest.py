import os

import pandas as pd

from src.backtest.simulation_engine import run_simulation
from src.backtest.logger import log_run_header
from src.market_data.historical_data import fetch_and_store_historical
from src.utils.file_util import read_config
from src.utils.grid_search import construct_strategy_param_grid
from src.utils.kite_client_util import normalize_interval

CONFIG_PATH = "config/config.yaml"
BACKTEST_CONFIG_PATH = "config/backtest-config.yaml"


def load_or_fetch_data(trading_symbol, interval_key, from_date, to_date):
    print(f"\n==============================================================================")
    filename = f"data/historical/{trading_symbol}_{interval_key}.csv"
    df = pd.DataFrame()

    if os.path.exists(filename):
        df = pd.read_csv(filename, parse_dates=['date'])
        print(f"✅ Loaded data for {trading_symbol} {interval_key} from {filename}")
        # return df
    else:
        print(f"⬇️ Data for {trading_symbol} {interval_key} not found, fetching...")
        fetch_and_store_historical(trading_symbol, from_date, to_date, interval_key)
        if os.path.exists(filename):
            df = pd.read_csv(filename, parse_dates=['date'])
            # return df
        else:
            print(f"❌ Failed to fetch data for {trading_symbol} {interval_key}")
            # return pd.DataFrame()
    print(f"==============================================================================")
    return df


def main():
    config = read_config(CONFIG_PATH)
    backtest_config = read_config(BACKTEST_CONFIG_PATH)

    backtest_cfg = backtest_config['backtest']
    data_cfg = backtest_cfg['data']
    strategies = backtest_cfg['strategies']
    simulation_params = backtest_cfg['simulation_params']
    debug_logs_flag = backtest_cfg.get('debug_logs', True)

    trading_symbols = data_cfg['trading_symbols']
    intervals = data_cfg['intervals']
    from_date = data_cfg['from_date']
    to_date = data_cfg['to_date']

    train_split = simulation_params.get('train_split', 1.0)
    initial_capital = simulation_params.get('initial_capital', 1000000)
    stop_loss_pct = simulation_params.get('stop_loss_pct', 0.02)
    trailing_stop_loss_pct = simulation_params.get('trailing_stop_loss_pct', 0.02)
    target_profit_pct = simulation_params.get('target_profit_pct', 0.04)
    hold_min_bars = simulation_params.get('hold_min_bars', 2)
    hold_max_bars = simulation_params.get('hold_max_bars', 120)
    contract_size = simulation_params.get('contract_size', 1)
    fill_rate = simulation_params.get('fill_rate', 1.0)
    slippage_pct = simulation_params.get('slippage_pct', 0.001)
    intraday_only = simulation_params.get('intraday_only', True)

    brokerage_cfg = config['brokerage']
    segment = brokerage_cfg.get('segment')
    exchange = brokerage_cfg.get('exchange')

    summary_metrics = []
    for trading_symbol in trading_symbols:
        for interval in intervals:
            interval_key = normalize_interval(interval)
            df = load_or_fetch_data(trading_symbol, interval_key, from_date, to_date)

            if df.empty:
                continue

            df.sort_values('date', inplace=True)
            df.reset_index(drop=True, inplace=True)

            # NOTE: The strategy engine is designed to work only on a single strategy each time for a particular df.
            for strategy in strategies:
                for strategy_params in construct_strategy_param_grid(strategy):
                    log_run_header(trading_symbol, interval, strategy_params)

                    _, metrics = run_simulation(
                        df,
                        strategy_params,
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
                        debug_logs_flag=debug_logs_flag,
                        save_results=True,
                        token=trading_symbol,
                        interval=interval_key,
                    )

                    # Save summary metrics for all splits (all/train/test)
                    for metric in metrics:
                        metric.update(dict(token=trading_symbol, interval=interval_key))
                        summary_metrics.append(metric)

    # Save all metrics summary
    if summary_metrics:
        os.makedirs("data/results", exist_ok=True)
        pd.DataFrame(summary_metrics).to_csv("data/results/metrics_summary.csv", index=False)
        print(f"\n==============================================================================")
        print("✅ All metrics summary saved to data/results/metrics_summary.csv")
        print(f"==============================================================================")


if __name__ == "__main__":
    main()
