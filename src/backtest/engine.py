import os
import pandas as pd
from src.backtest.signals import compute_ema_signals
from src.backtest.metrics import compute_metrics
from src.utils.brokerage import calculate_brokerage
from src.backtest.logger import log_trade, log_metrics, log_run_header

def run_backtest(
        df,
        strategy_name,
        fast,
        slow,
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
        train_split=1.0,
        intraday_only=True,
        verbose=True,
        save_results=True,
        token="",
        interval=""
):
    df = df.copy()
    compute_ema_signals(df, fast, slow)  # Lookahead safe

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
            split_df,
            fast, slow, initial_capital,
            stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
            contract_size, hold_min_bars, hold_max_bars, fill_rate,
            slippage_pct, segment, exchange, intraday_only, verbose
        )
        metrics = compute_metrics(trades, equity_curve, initial_capital, split_df)
        if verbose:
            log_metrics(metrics, token, interval, fast, slow, split_name)
        # Save trade details
        if save_results and split_name == 'all' and len(trades) > 0:
            out_dir = "data/results"
            os.makedirs(out_dir, exist_ok=True)
            trades_df = pd.DataFrame(trades)
            trades_df.to_csv(f"{out_dir}/trades_{token}_{interval}_{strategy_name}_{fast}-{slow}.csv", index=False)
        all_trades.extend(trades)
        metrics['split'] = split_name
        all_metrics.append(metrics)
    return all_trades, all_metrics

def simulate_strategy(
        df,
        fast, slow, initial_capital,
        stop_loss_pct, trailing_stop_loss_pct, target_profit_pct,
        contract_size, hold_min_bars, hold_max_bars, fill_rate,
        slippage_pct, segment, exchange, intraday_only, verbose
):
    capital = initial_capital
    equity_curve = []
    position = None  # None | "LONG" | "SHORT"
    entry_idx = -1
    entry_price = 0
    entry_time = None
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
        price = row['close']
        date = row['date']
        signal_long = row['EMA_CROSS_SIGNAL']
        signal_short = row['EMA_CROSS_SIGNAL_SHORT']
        high = row['high']
        low = row['low']
        is_last_bar = (i == len(df) - 1)
        next_day = (i+1 < len(df)) and (row['date'].date() != df.iloc[i+1]['date'].date())
        eod_exit = intraday_only and (is_last_bar or next_day)

        # ENTRY LOGIC
        if position is None:
            # Check for LONG ENTRY
            if signal_long == 1 and (last_signal != 1):
                position = "LONG"
                entry_idx = i
                entry_price = price * (1 + slippage_pct)
                entry_time = date
                qty = int((capital * fill_rate) // (entry_price * contract_size)) * contract_size
                if qty == 0:
                    trade = None
                    continue
                stop_price = entry_price * (1 - stop_loss_pct) if stop_loss_pct else None
                trail_high = entry_price
                target_price = entry_price * (1 + target_profit_pct) if target_profit_pct else None
                bars_held = 0
                trade = dict(
                    direction="LONG",
                    entry_time=entry_time,
                    entry_price=entry_price,
                    qty=qty,
                    exit_time=None,
                    exit_price=None,
                    exit_reason=None,
                    pnl=0.0,
                )
                # if verbose:
                #     log_trade("ENTRY", trade, i)
            # Check for SHORT ENTRY
            elif signal_short == 1 and (last_signal != -1):
                position = "SHORT"
                entry_idx = i
                entry_price = price * (1 - slippage_pct)
                entry_time = date
                qty = int((capital * fill_rate) // (entry_price * contract_size)) * contract_size
                if qty == 0:
                    trade = None
                    continue
                stop_price = entry_price * (1 + stop_loss_pct) if stop_loss_pct else None
                trail_low = entry_price
                target_price = entry_price * (1 - target_profit_pct) if target_profit_pct else None
                bars_held = 0
                trade = dict(
                    direction="SHORT",
                    entry_time=entry_time,
                    entry_price=entry_price,
                    qty=qty,
                    exit_time=None,
                    exit_price=None,
                    exit_reason=None,
                    pnl=0.0,
                )
                # if verbose:
                #     log_trade("ENTRY", trade, i)
        else:
            bars_held += 1
            exit_price = None
            reason = None
            # LONG MANAGEMENT
            if position == "LONG":
                # Trailing stop for long
                if trailing_stop_loss_pct:
                    if trail_high is not None and high > trail_high:
                        trail_high = high
                    new_stop = trail_high * (1 - trailing_stop_loss_pct) if trail_high is not None else None
                    if stop_price is None or (new_stop is not None and new_stop > stop_price):
                        stop_price = new_stop
                # Exit if stop loss hit
                if stop_price is not None and low <= stop_price:
                    exit_price = stop_price * (1 - slippage_pct)
                    reason = "STOP LOSS"
                # Exit if target hit
                elif target_price is not None and high >= target_price:
                    exit_price = target_price * (1 - slippage_pct)
                    reason = "TARGET"
                # Exit on signal cross down (with hold min logic)
                elif signal_long == 0 and (bars_held >= hold_min_bars):
                    exit_price = price * (1 - slippage_pct)
                    reason = "EMA CROSS DOWN"
                # Exit if max bars held
                elif hold_max_bars and bars_held >= hold_max_bars:
                    exit_price = price * (1 - slippage_pct)
                    reason = "MAX HOLD"
                # END OF DAY (new fix: always as separate check)
                if not exit_price and eod_exit:
                    exit_price = price * (1 - slippage_pct)
                    reason = "END OF DAY"
                # If exit triggered and trade is valid
                if exit_price is not None and trade is not None:
                    cost_buy = calculate_brokerage(segment, "BUY", entry_price, qty, exchange)['total']
                    cost_sell = calculate_brokerage(segment, "SELL", exit_price, qty, exchange)['total']
                    pnl = (exit_price - entry_price) * qty - cost_buy - cost_sell
                    trade.update(dict(
                        exit_time=date,
                        exit_price=exit_price,
                        exit_reason=reason,
                        pnl=pnl
                    ))
                    trades.append(trade)
                    capital += pnl
                    # if verbose:
                    #     log_trade("EXIT", trade, i)
                    position = None
                    bars_held = 0
                    entry_price = None
                    qty = 0
                    stop_price = None
                    target_price = None
                    trail_high = None
                    trade = None
            # SHORT MANAGEMENT
            elif position == "SHORT":
                if trailing_stop_loss_pct:
                    if trail_low is not None and low < trail_low:
                        trail_low = low
                    new_stop = trail_low * (1 + trailing_stop_loss_pct) if trail_low is not None else None
                    if stop_price is None or (new_stop is not None and new_stop < stop_price):
                        stop_price = new_stop
                # Exit if stop loss hit
                if stop_price is not None and high >= stop_price:
                    exit_price = stop_price * (1 + slippage_pct)
                    reason = "STOP LOSS"
                # Exit if target hit
                elif target_price is not None and low <= target_price:
                    exit_price = target_price * (1 + slippage_pct)
                    reason = "TARGET"
                # Exit on signal cross up (with hold min logic)
                elif signal_short == 0 and (bars_held >= hold_min_bars):
                    exit_price = price * (1 + slippage_pct)
                    reason = "EMA CROSS UP"
                # Exit if max bars held
                elif hold_max_bars and bars_held >= hold_max_bars:
                    exit_price = price * (1 + slippage_pct)
                    reason = "MAX HOLD"
                # END OF DAY (new fix: always as separate check)
                if not exit_price and eod_exit:
                    exit_price = price * (1 + slippage_pct)
                    reason = "END OF DAY"
                if exit_price is not None and trade is not None:
                    cost_sell = calculate_brokerage(segment, "SELL", entry_price, qty, exchange)['total']
                    cost_buy = calculate_brokerage(segment, "BUY", exit_price, qty, exchange)['total']
                    pnl = (entry_price - exit_price) * qty - cost_buy - cost_sell
                    trade.update(dict(
                        exit_time=date,
                        exit_price=exit_price,
                        exit_reason=reason,
                        pnl=pnl
                    ))
                    trades.append(trade)
                    capital += pnl
                    # if verbose:
                    #     log_trade("EXIT", trade, i)
                    position = None
                    bars_held = 0
                    entry_price = None
                    qty = 0
                    stop_price = None
                    target_price = None
                    trail_low = None
                    trade = None
        last_signal = 1 if signal_long == 1 else (-1 if signal_short == 1 else 0)
        equity_curve.append(dict(date=date, equity=capital))
    return trades, equity_curve
