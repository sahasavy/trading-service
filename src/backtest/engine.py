import os
import pandas as pd
from src.backtest.signals import compute_ema_signals
from src.backtest.metrics import compute_metrics
from src.commons.constants.constants import OrderPosition, TradeEvent, OrderSide, TradeExitReason
from src.utils.brokerage_util import calculate_brokerage
from src.backtest.logger import log_trade, log_metrics


def run_backtest(
        df, strategy_name, fast, slow, initial_capital,
        stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
        contract_size, hold_min_bars, hold_max_bars, fill_rate,
        slippage_pct, segment, exchange, train_split=1.0, intraday_only=True,
        debug_logs_flag=True, save_results=True, token="", interval=""
):
    df = df.copy()
    compute_ema_signals(df, fast, slow)
    split_idx = int(len(df) * train_split)
    splits = [
        ('all', df),
        ('train', df.iloc[:split_idx]),
        ('test', df.iloc[split_idx:]) if train_split < 1.0 else None
    ]

    all_trades = []
    all_metrics = []
    for split_name, split_df in filter(None, splits):
        trades, equity_curve = simulate_strategy(
            split_df, initial_capital, stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
            contract_size, hold_min_bars, hold_max_bars, fill_rate,
            slippage_pct, segment, exchange, intraday_only, debug_logs_flag
        )

        metrics = compute_metrics(trades, equity_curve, initial_capital, split_df)
        if debug_logs_flag:
            log_metrics(metrics, token, interval, fast, slow, split_name)

        # Save trade details
        if save_results and split_name == 'all' and len(trades) > 0:
            out_dir = "data/results"
            os.makedirs(out_dir, exist_ok=True)
            trades_df = pd.DataFrame(trades)
            filename = f"{out_dir}/trades_{token}_{interval}_{strategy_name}_{fast}-{slow}.csv"
            trades_df.to_csv(filename, index=False)

        all_trades.extend(trades)
        metrics['split'] = split_name
        all_metrics.append(metrics)
    return all_trades, all_metrics


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
                     stop_price, trail_high, target_price, slippage_pct, eod_exit):
    high, low, price = row['high'], row['low'], row['close']
    reason, exit_price = None, None
    # Trailing stop
    if trailing_stop_loss_pct:
        if trail_high is not None and high > trail_high:
            trail_high = high
        new_stop = trail_high * (1 - trailing_stop_loss_pct) if trail_high is not None else None
        if stop_price is None or (new_stop is not None and new_stop > stop_price):
            stop_price = new_stop
    # Stop loss
    if stop_price is not None and low <= stop_price:
        exit_price = stop_price * (1 - slippage_pct)
        reason = TradeExitReason.STOP_LOSS.name
    elif target_price is not None and high >= target_price:
        exit_price = target_price * (1 - slippage_pct)
        reason = TradeExitReason.TARGET.name
    elif row['EMA_CROSS_SIGNAL_LONG'] == 0 and (bars_held >= hold_min_bars):
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
                      stop_price, trail_low, target_price, slippage_pct, eod_exit):
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
    elif row['EMA_CROSS_SIGNAL_SHORT'] == 0 and (bars_held >= hold_min_bars):
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


def simulate_strategy(
        df, initial_capital,
        stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
        contract_size, hold_min_bars, hold_max_bars, fill_rate,
        slippage_pct, segment, exchange, intraday_only, debug_logs_flag
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
        signal_long = row['EMA_CROSS_SIGNAL_LONG']
        signal_short = row['EMA_CROSS_SIGNAL_SHORT']
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
                        log_trade(TradeEvent.ENTRY.name, trade, i)
            elif signal_short == 1 and (last_signal != -1):
                trade, entry_price, qty, stop_price, target_price, trail_low = try_short_entry(
                    row, capital, fill_rate, contract_size, slippage_pct, stop_loss_pct, target_profit_pct
                )
                if trade is not None:
                    position = OrderPosition.SHORT.name
                    bars_held = 0
                    if debug_logs_flag:
                        log_trade(TradeEvent.ENTRY.name, trade, i)
        else:
            bars_held += 1
            exit_price = None
            reason = None
            if position == OrderPosition.LONG.name:
                exit_price, reason, stop_price, trail_high = manage_long_exit(
                    row, bars_held, hold_min_bars, hold_max_bars, trailing_stop_loss_pct,
                    stop_price, trail_high, target_price, slippage_pct, eod_exit
                )
                if exit_price is not None and trade is not None:
                    cost_buy = calculate_brokerage(segment, OrderSide.BUY.name, entry_price, qty, exchange)['total']
                    cost_sell = calculate_brokerage(segment, OrderSide.SELL.name, exit_price, qty, exchange)['total']
                    pnl = (exit_price - entry_price) * qty - cost_buy - cost_sell
                    trade.update(dict(exit_time=row['date'], exit_price=exit_price, exit_reason=reason, pnl=pnl))
                    trades.append(trade)
                    capital += pnl
                    if debug_logs_flag:
                        log_trade(TradeEvent.EXIT.name, trade, i)
                    position, bars_held, entry_price, qty, stop_price, target_price, trail_high, trail_low = reset_state()
            elif position == OrderPosition.SHORT.name:
                exit_price, reason, stop_price, trail_low = manage_short_exit(
                    row, bars_held, hold_min_bars, hold_max_bars, trailing_stop_loss_pct,
                    stop_price, trail_low, target_price, slippage_pct, eod_exit
                )
                if exit_price is not None and trade is not None:
                    cost_sell = calculate_brokerage(segment, OrderSide.SELL.name, entry_price, qty, exchange)['total']
                    cost_buy = calculate_brokerage(segment, OrderSide.BUY.name, exit_price, qty, exchange)['total']
                    pnl = (entry_price - exit_price) * qty - cost_buy - cost_sell
                    trade.update(dict(exit_time=row['date'], exit_price=exit_price, exit_reason=reason, pnl=pnl))
                    trades.append(trade)
                    capital += pnl
                    if debug_logs_flag:
                        log_trade(TradeEvent.EXIT.name, trade, i)
                    position, bars_held, entry_price, qty, stop_price, target_price, trail_high, trail_low = reset_state()
        last_signal = 1 if signal_long == 1 else (-1 if signal_short == 1 else 0)
        equity_curve.append(dict(date=row['date'], equity=capital))
    return trades, equity_curve
