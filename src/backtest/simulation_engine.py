import os

import pandas as pd

from src.commons.constants.constants import OrderPosition, TradeEvent, OrderSide, TradeExitReason, DataframeSplit
from src.indicators.registry import add_signals
from src.utils.backtest_util import construct_strategy_hyperparam_str
from src.utils.brokerage_util import calculate_brokerage
from src.utils.file_util import save_df_to_csv, get_trades_dir, get_features_dir
from src.utils.logger_util import log_backtest_trade, log_backtest_metrics
from src.utils.metrics_util import compute_backtest_metrics
from src.utils.visualization_util import add_visualizations


def get_signal_column_names(strategy_name):
    """Returns the actual column names for LONG and SHORT signals for the given strategy."""
    prefix = strategy_name.upper()
    long_col = f"{prefix}_LONG_SIGNAL"
    short_col = f"{prefix}_SHORT_SIGNAL"
    return long_col, short_col


def run_simulation(
        df, strategy_params, initial_capital,
        stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
        contract_size, hold_min_bars, hold_max_bars, fill_rate,
        slippage_pct, segment, exchange, train_split=1.0, intraday_only=True,
        debug_logs_flag=True, save_results=True, trading_symbol="", interval="", sim_dir=None
):
    # Always re-add signals per param set
    df_per_strategy = df.copy()

    strategy_name = strategy_params['name']
    add_signals(df_per_strategy, strategy_name,
                {hyperparam_key: hyperparam_value for hyperparam_key, hyperparam_value in strategy_params.items() if
                 hyperparam_key != 'name'})

    strategy_hyperparam_str = construct_strategy_hyperparam_str(strategy_params)
    filename = f"{trading_symbol}_{interval}_{strategy_params['name']}_{strategy_hyperparam_str}.csv"

    df_per_strategy.dropna(inplace=True)
    df_per_strategy.reset_index(drop=True, inplace=True)

    features_dir = get_features_dir(sim_dir)
    features_file_path = os.path.join(features_dir, filename)
    save_df_to_csv(df_per_strategy, features_file_path)

    long_signal_col, short_signal_col = get_signal_column_names(strategy_name)

    split_idx = int(len(df_per_strategy) * train_split)
    splits = [
        (DataframeSplit.ALL.name, df_per_strategy),
        (DataframeSplit.TRAIN.name, df_per_strategy.iloc[:split_idx]),
        (DataframeSplit.TEST.name, df_per_strategy.iloc[split_idx:]) if train_split < 1.0 else None
    ]

    all_trades = []
    all_metrics = []
    equity_curve_for_all = None
    for split_name, split_df in filter(None, splits):
        trades, equity_curve = simulate_strategy(
            split_df, initial_capital, stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
            contract_size, hold_min_bars, hold_max_bars, fill_rate,
            slippage_pct, segment, exchange, intraday_only, debug_logs_flag,
            long_signal_col, short_signal_col
        )

        if split_name == DataframeSplit.ALL.name:
            equity_curve_for_all = equity_curve

        # Generate Metrics
        metrics = compute_backtest_metrics(trades, equity_curve, initial_capital, split_df)
        if debug_logs_flag:
            log_backtest_metrics(metrics, trading_symbol, interval, strategy_params, split_name)

        # TODO - Generate Visualizations (temporarily commented out)
        # if save_results and split_name == DataframeSplit.ALL.name and len(trades) > 0 and sim_dir:
        #     add_visualizations(trading_symbol, interval, sim_dir, strategy_params, equity_curve, trades, split_df)

        # Save trade details
        if save_results and split_name == DataframeSplit.ALL.name and len(trades) > 0:
            trade_dir = get_trades_dir(sim_dir)
            trades_file_path = os.path.join(trade_dir, filename)
            trades_df = pd.DataFrame(trades)
            save_df_to_csv(trades_df, trades_file_path)

        all_trades.extend(trades)
        metrics['split'] = split_name
        metrics['strategy'] = strategy_params['name']
        metrics.update(
            {hyperparam_key: hyperparam_value for hyperparam_key, hyperparam_value in strategy_params.items() if
             hyperparam_key != 'name'})
        all_metrics.append(metrics)
    return all_trades, all_metrics, equity_curve_for_all


def simulate_strategy(
        df, initial_capital,
        stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
        contract_size, hold_min_bars, hold_max_bars, fill_rate,
        slippage_pct, segment, exchange, intraday_only, debug_logs_flag,
        long_signal_col, short_signal_col
):
    capital = initial_capital
    equity_curve = []
    position = None
    entry_price = 0
    qty = 0
    stop_price = None
    target_price = None
    trail_high = None
    trail_low = None
    trades = []
    bars_held = 0
    last_signal = 0  # 1=long, -1=short, 0=none
    trade = None

    for i, row in df.iterrows():
        signal_long = row.get(long_signal_col, 0)
        signal_short = row.get(short_signal_col, 0)
        is_last_bar = (i == len(df) - 1)
        next_day = (i + 1 < len(df)) and (row['date'].date() != df.iloc[i + 1]['date'].date())
        eod_exit = intraday_only and (is_last_bar or next_day)

        # ENTRY LOGIC
        if position is None:
            if signal_long == 1 and (last_signal != 1):
                trade, entry_price, qty, stop_price, target_price, trail_high = try_long_entry(
                    row, capital, fill_rate, contract_size, slippage_pct, stop_loss_pct, target_profit_pct
                )
                if trade is not None:
                    position = OrderPosition.LONG.name
                    bars_held = 0
                    if debug_logs_flag:
                        log_backtest_trade(TradeEvent.ENTRY.name, trade, i)
            elif signal_short == 1 and (last_signal != -1):
                trade, entry_price, qty, stop_price, target_price, trail_low = try_short_entry(
                    row, capital, fill_rate, contract_size, slippage_pct, stop_loss_pct, target_profit_pct
                )
                if trade is not None:
                    position = OrderPosition.SHORT.name
                    bars_held = 0
                    if debug_logs_flag:
                        log_backtest_trade(TradeEvent.ENTRY.name, trade, i)
        else:
            bars_held += 1
            exit_price = None
            reason = None
            if position == OrderPosition.LONG.name:
                exit_price, reason, stop_price, trail_high = manage_long_exit(
                    row, bars_held, hold_min_bars, hold_max_bars, trailing_stop_loss_pct,
                    stop_price, trail_high, target_price, slippage_pct, eod_exit,
                    long_signal_col=long_signal_col
                )
                if exit_price is not None and trade is not None:
                    cost_buy = calculate_brokerage(segment, OrderSide.BUY.name, entry_price, qty, exchange)['total']
                    cost_sell = calculate_brokerage(segment, OrderSide.SELL.name, exit_price, qty, exchange)['total']
                    pnl = (exit_price - entry_price) * qty - cost_buy - cost_sell
                    trade.update(dict(exit_time=row['date'], exit_price=exit_price, exit_reason=reason, pnl=pnl))
                    trades.append(trade)
                    capital += pnl
                    if debug_logs_flag:
                        log_backtest_trade(TradeEvent.EXIT.name, trade, i)
                    position, bars_held, entry_price, qty, stop_price, target_price, trail_high, trail_low = reset_state()
            elif position == OrderPosition.SHORT.name:
                exit_price, reason, stop_price, trail_low = manage_short_exit(
                    row, bars_held, hold_min_bars, hold_max_bars, trailing_stop_loss_pct,
                    stop_price, trail_low, target_price, slippage_pct, eod_exit,
                    short_signal_col=short_signal_col
                )
                if exit_price is not None and trade is not None:
                    cost_sell = calculate_brokerage(segment, OrderSide.SELL.name, entry_price, qty, exchange)['total']
                    cost_buy = calculate_brokerage(segment, OrderSide.BUY.name, exit_price, qty, exchange)['total']
                    pnl = (entry_price - exit_price) * qty - cost_buy - cost_sell
                    trade.update(dict(exit_time=row['date'], exit_price=exit_price, exit_reason=reason, pnl=pnl))
                    trades.append(trade)
                    capital += pnl
                    if debug_logs_flag:
                        log_backtest_trade(TradeEvent.EXIT.name, trade, i)
                    position, bars_held, entry_price, qty, stop_price, target_price, trail_high, trail_low = reset_state()
        last_signal = 1 if signal_long == 1 else (-1 if signal_short == 1 else 0)
        equity_curve.append(dict(date=row['date'], equity=capital))
    return trades, equity_curve


def try_long_entry(row, capital, fill_rate, contract_size, slippage_pct, stop_loss_pct, target_profit_pct):
    price = row['close']
    entry_price = price * (1 + slippage_pct)
    qty = int((capital * fill_rate) // (entry_price * contract_size)) * contract_size
    if qty == 0:
        return None, None, None, None, None, None
    stop_price = entry_price * (1 - stop_loss_pct) if stop_loss_pct else None
    trail_high = entry_price
    target_price = entry_price * (1 + target_profit_pct) if target_profit_pct else None
    trade = dict(
        direction=OrderPosition.LONG.name,
        entry_time=row['date'],
        entry_price=entry_price,
        qty=qty,
        exit_time=None,
        exit_price=None,
        exit_reason=None,
        pnl=0.0,
    )
    return trade, entry_price, qty, stop_price, target_price, trail_high


def try_short_entry(row, capital, fill_rate, contract_size, slippage_pct, stop_loss_pct, target_profit_pct):
    price = row['close']
    entry_price = price * (1 - slippage_pct)
    qty = int((capital * fill_rate) // (entry_price * contract_size)) * contract_size
    if qty == 0:
        return None, None, None, None, None, None
    stop_price = entry_price * (1 + stop_loss_pct) if stop_loss_pct else None
    trail_low = entry_price
    target_price = entry_price * (1 - target_profit_pct) if target_profit_pct else None
    trade = dict(
        direction=OrderPosition.SHORT.name,
        entry_time=row['date'],
        entry_price=entry_price,
        qty=qty,
        exit_time=None,
        exit_price=None,
        exit_reason=None,
        pnl=0.0,
    )
    return trade, entry_price, qty, stop_price, target_price, trail_low


def manage_long_exit(row, bars_held, hold_min_bars, hold_max_bars, trailing_stop_loss_pct,
                     stop_price, trail_high, target_price, slippage_pct, eod_exit,
                     long_signal_col='LONG_SIGNAL'):
    high, low, price = row['high'], row['low'], row['close']
    reason, exit_price = None, None
    if trailing_stop_loss_pct:
        if trail_high is not None and high > trail_high:
            trail_high = high
        new_stop = trail_high * (1 - trailing_stop_loss_pct) if trail_high is not None else None
        if stop_price is None or (new_stop is not None and new_stop > stop_price):
            stop_price = new_stop
    if stop_price is not None and low <= stop_price:
        exit_price = stop_price * (1 - slippage_pct)
        reason = TradeExitReason.STOP_LOSS.name
    elif target_price is not None and high >= target_price:
        exit_price = target_price * (1 - slippage_pct)
        reason = TradeExitReason.TARGET.name
    elif row[long_signal_col] == 0 and (bars_held >= hold_min_bars):
        exit_price = price * (1 - slippage_pct)
        reason = TradeExitReason.CROSS_DOWN.name
    elif hold_max_bars and bars_held >= hold_max_bars:
        exit_price = price * (1 - slippage_pct)
        reason = TradeExitReason.MAX_HOLD.name
    if not exit_price and eod_exit:
        exit_price = price * (1 - slippage_pct)
        reason = TradeExitReason.EOD.name
    return exit_price, reason, stop_price, trail_high


def manage_short_exit(row, bars_held, hold_min_bars, hold_max_bars, trailing_stop_loss_pct,
                      stop_price, trail_low, target_price, slippage_pct, eod_exit,
                      short_signal_col='SHORT_SIGNAL'):
    high, low, price = row['high'], row['low'], row['close']
    reason, exit_price = None, None
    if trailing_stop_loss_pct:
        if trail_low is not None and low < trail_low:
            trail_low = low
        new_stop = trail_low * (1 + trailing_stop_loss_pct) if trail_low is not None else None
        if stop_price is None or (new_stop is not None and new_stop < stop_price):
            stop_price = new_stop
    if stop_price is not None and high >= stop_price:
        exit_price = stop_price * (1 + slippage_pct)
        reason = TradeExitReason.STOP_LOSS.name
    elif target_price is not None and low <= target_price:
        exit_price = target_price * (1 + slippage_pct)
        reason = TradeExitReason.TARGET.name
    elif row[short_signal_col] == 0 and (bars_held >= hold_min_bars):
        exit_price = price * (1 + slippage_pct)
        reason = TradeExitReason.CROSS_UP.name
    elif hold_max_bars and bars_held >= hold_max_bars:
        exit_price = price * (1 + slippage_pct)
        reason = TradeExitReason.MAX_HOLD.name
    if not exit_price and eod_exit:
        exit_price = price * (1 + slippage_pct)
        reason = TradeExitReason.EOD.name
    return exit_price, reason, stop_price, trail_low


def reset_state():
    return None, 0, None, 0, None, None, None, None
