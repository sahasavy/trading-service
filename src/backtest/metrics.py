import numpy as np
import pandas as pd


def compute_metrics(trades, equity_curve, initial_capital, df):
    # Total return
    final_equity = equity_curve[-1]['equity'] if equity_curve else initial_capital
    total_return = (final_equity - initial_capital) / initial_capital * 100

    # Annualized return
    days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
    years = days / 365.25 if days > 0 else 1
    cagr = ((final_equity / initial_capital) ** (1 / years)) - 1 if years > 0 else 0

    # Equity curve as pd.Series
    eq_series = pd.Series([x['equity'] for x in equity_curve])
    # Daily returns for volatility & Sharpe
    eq_curve = pd.DataFrame(equity_curve)
    eq_curve['date'] = pd.to_datetime(eq_curve['date'])
    eq_curve.set_index('date', inplace=True)
    daily_eq = eq_curve['equity'].resample('1D').last().ffill()
    daily_returns = daily_eq.pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) if not daily_returns.empty else 0
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0

    # Max drawdown
    running_max = eq_series.cummax()
    drawdowns = (eq_series - running_max) / running_max
    max_drawdown = drawdowns.min() * 100 if not drawdowns.empty else 0

    # Trades metrics
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] < 0]
    num_trades = len(trades)
    win_rate = len(wins) / num_trades * 100 if num_trades else 0
    profit_factor = (sum([t['pnl'] for t in wins]) / abs(sum([t['pnl'] for t in losses]))) if losses else 0

    # Exposure: percent of bars in market
    bars_with_pos = 0
    pos = False
    for t in trades:
        if t['entry_time'] and t['exit_time']:
            bars = (t['exit_time'] - t['entry_time']).total_seconds() / (
                (df['date'].iloc[1] - df['date'].iloc[0]).total_seconds())
            bars_with_pos += bars if bars > 0 else 1
    exposure = (bars_with_pos / len(df)) * 100 if len(df) else 0

    return dict(
        total_return=total_return,
        cagr=cagr * 100,
        volatility=volatility * 100,
        sharpe=sharpe,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        profit_factor=profit_factor,
        trades=num_trades,
        exposure=exposure,
    )
