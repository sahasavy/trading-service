import numpy as np
import pandas as pd

from src.utils.logger_util import log_backtest_metrics


def generate_simulation_results(equity_curve, initial_capital, interval, split_df, split_name, strategy_params, trades,
                                trading_symbol, debug_logs_flag):
    metrics = {
        'token': trading_symbol,
        'interval': interval,
        'split': split_name,
        'strategy': strategy_params['name']
    }
    metrics.update({hyperparam_key: hyperparam_value for hyperparam_key, hyperparam_value in strategy_params.items() if
                    hyperparam_key != 'name'})
    metrics.update(compute_backtest_metrics(trades, equity_curve, initial_capital, split_df))

    if debug_logs_flag:
        log_backtest_metrics(metrics, trading_symbol, interval, strategy_params, split_name)

    return metrics


def compute_backtest_metrics(trades, equity_curve, initial_capital, df):
    # --- Core Returns ---
    gross_pnl = sum([t.get('gross_pnl', 0) for t in trades])
    total_fees = sum([t.get('total_fee', 0) for t in trades])
    net_pnl = sum([t.get('pnl', 0) for t in trades])  # or gross_pnl - total_fees
    final_equity = equity_curve[-1]['equity'] if equity_curve else initial_capital
    equity_final = final_equity
    total_return = (final_equity - initial_capital) / initial_capital * 100

    # --- CAGR ---
    days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
    years = days / 365.25 if days > 0 else 1
    cagr = ((final_equity / initial_capital) ** (1 / years)) - 1 if years > 0 else 0

    # --- Equity Series ---
    eq_series = pd.Series([x['equity'] for x in equity_curve])
    eq_curve = pd.DataFrame(equity_curve)
    eq_curve['date'] = pd.to_datetime(eq_curve['date'])
    eq_curve.set_index('date', inplace=True)
    daily_eq = eq_curve['equity'].resample('1D').last().ffill()
    daily_returns = daily_eq.pct_change().dropna()

    # --- Sharpe Ratio ---
    volatility = daily_returns.std() * np.sqrt(252) if not daily_returns.empty else 0
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0

    # --- Sortino Ratio ---
    downside_returns = daily_returns[daily_returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252) if not downside_returns.empty else 0
    sortino = (daily_returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0

    # --- Max Drawdown & Calmar Ratio ---
    running_max = eq_series.cummax()
    drawdowns = (eq_series - running_max) / running_max
    max_drawdown = drawdowns.min() * 100 if not drawdowns.empty else 0
    calmar = (cagr * 100) / abs(max_drawdown) if max_drawdown != 0 else 0

    # --- Monthly Returns Table ---
    monthly_returns = daily_eq.resample('ME').last().pct_change().fillna(0) * 100
    monthly_return_table = monthly_returns.to_dict()

    # --- Trades Metrics ---
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] < 0]
    num_trades = len(trades)
    win_rate = len(wins) / num_trades * 100 if num_trades else 0
    profit_factor = (sum([t['pnl'] for t in wins]) / abs(sum([t['pnl'] for t in losses]))) if losses else 0
    avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
    avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
    expectancy = ((win_rate / 100) * avg_win + (1 - win_rate / 100) * avg_loss) if num_trades else 0
    best_trade = max([t['pnl'] for t in trades], default=0)
    worst_trade = min([t['pnl'] for t in trades], default=0)
    median_trade = np.median([t['pnl'] for t in trades]) if trades else 0

    # --- Holding Period Analysis ---
    holding_periods = [
        (t['exit_time'] - t['entry_time']).total_seconds() / 60  # in minutes
        for t in trades if t['exit_time'] and t['entry_time']
    ]
    avg_holding = np.mean(holding_periods) if holding_periods else 0
    median_holding = np.median(holding_periods) if holding_periods else 0

    # --- Exposure: percent of bars in market ---
    bars_with_pos = 0
    for t in trades:
        if t['entry_time'] and t['exit_time']:
            bars = (t['exit_time'] - t['entry_time']).total_seconds() / (
                (df['date'].iloc[1] - df['date'].iloc[0]).total_seconds())
            bars_with_pos += bars if bars > 0 else 1
    exposure = (bars_with_pos / len(df)) * 100 if len(df) else 0

    # --- Streaks ---
    streaks = []
    curr = None
    streak = 0
    for t in trades:
        if t['pnl'] > 0:
            if curr == 'win':
                streak += 1
            else:
                streak = 1
                curr = 'win'
        elif t['pnl'] < 0:
            if curr == 'loss':
                streak += 1
            else:
                streak = 1
                curr = 'loss'
        else:
            streak = 0
            curr = None
        streaks.append((curr, streak))
    max_win_streak = max((s for c, s in streaks if c == 'win'), default=0)
    max_loss_streak = max((s for c, s in streaks if c == 'loss'), default=0)

    return dict(
        gross_pnl=gross_pnl,
        total_fees=total_fees,
        net_pnl=net_pnl,
        equity_final=equity_final,
        total_return=total_return,
        win_rate=win_rate,
        profit_factor=profit_factor,
        trades=num_trades,
        best_trade=best_trade,
        worst_trade=worst_trade,
        median_trade=median_trade,
        avg_win=avg_win,
        avg_loss=avg_loss,
        expectancy=expectancy,
        exposure=exposure,
        avg_holding=avg_holding,
        median_holding=median_holding,
        max_win_streak=max_win_streak,
        max_loss_streak=max_loss_streak,
        cagr=cagr * 100,
        volatility=volatility * 100,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown=max_drawdown,
        calmar=calmar,
        monthly_returns=monthly_return_table,
    )
