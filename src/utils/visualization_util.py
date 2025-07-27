import os
import matplotlib.pyplot as plt
import pandas as pd

from src.commons.constants.constants import OrderPosition


def add_visualizations(trading_symbol, interval, sim_dir, strategy_params, equity_curve):
    plot_dir = os.path.join(sim_dir, 'plots')
    os.makedirs(plot_dir, exist_ok=True)
    prefix = f"{trading_symbol}_{interval}_{strategy_params['name']}"

    # 1. Equity Curve
    eq_path = os.path.join(plot_dir, f"{prefix}_equity_curve.png")
    plot_equity_curve(equity_curve, save_path=eq_path,
                      title=f"Equity Curve - {trading_symbol} {interval} {strategy_params['name']}")
    # 2. Drawdown Curve
    dd_path = os.path.join(plot_dir, f"{prefix}_drawdown.png")
    plot_drawdown(equity_curve, save_path=dd_path,
                  title=f"Drawdown - {trading_symbol} {interval} {strategy_params['name']}")
    # 3. Daily Returns
    dr_path = os.path.join(plot_dir, f"{prefix}_daily_returns.png")
    plot_daily_returns(equity_curve, save_path=dr_path,
                       title=f"Daily Returns - {trading_symbol} {interval} {strategy_params['name']}")
    # 4. Monthly Returns
    mr_path = os.path.join(plot_dir, f"{prefix}_monthly_returns.png")
    plot_monthly_returns(equity_curve, save_path=mr_path,
                         title=f"Monthly Returns - {trading_symbol} {interval} {strategy_params['name']}")


def plot_equity_curve(equity_curve, save_path=None, show=False, title='Equity Curve'):
    """
    Equity Curve: Shows portfolio value over time.
    """
    plt.figure(figsize=(12, 5))
    if isinstance(equity_curve, pd.DataFrame):
        equity_curve = equity_curve.copy()
        equity_curve['date'] = pd.to_datetime(equity_curve['date'])
        x = equity_curve['date']
        y = equity_curve['equity']
    elif isinstance(equity_curve, list):
        x = [pd.to_datetime(e['date']) for e in equity_curve]
        y = [e['equity'] for e in equity_curve]
    else:
        raise ValueError("Unsupported equity_curve type")

    plt.plot(x, y, label='Equity')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Equity')
    plt.grid()
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def plot_drawdown(equity_curve, save_path=None, show=False, title='Drawdown Curve'):
    """
    Drawdown: Shows the % drop from previous peaks.
    """
    if isinstance(equity_curve, list):
        df = pd.DataFrame(equity_curve)
    else:
        df = equity_curve.copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    running_max = df['equity'].cummax()
    drawdown = (df['equity'] - running_max) / running_max * 100

    plt.figure(figsize=(12, 4))
    plt.fill_between(drawdown.index, drawdown.values, color='red', alpha=0.4)
    plt.title(title)
    plt.ylabel('Drawdown (%)')
    plt.xlabel('Date')
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def plot_daily_returns(df, save_path=None, show=False, title='Daily Returns (%)'):
    """
    Daily Returns: Day-by-day percentage return (volatility, outliers visible).
    """
    eq_df = pd.DataFrame(df)
    eq_df['date'] = pd.to_datetime(eq_df['date'])
    eq_df.set_index('date', inplace=True)
    daily_eq = eq_df['equity'].resample('1D').last().ffill()
    daily_returns = daily_eq.pct_change() * 100
    plt.figure(figsize=(12, 4))
    plt.plot(daily_returns.index, daily_returns.values)
    plt.title(title)
    plt.ylabel('Daily Return (%)')
    plt.xlabel('Date')
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def plot_monthly_returns(df, save_path=None, show=False, title='Monthly Returns (%)'):
    """
    Monthly Returns: Bar plot for each month’s net return.
    """
    eq_df = pd.DataFrame(df)
    eq_df['date'] = pd.to_datetime(eq_df['date'])
    eq_df.set_index('date', inplace=True)
    monthly_eq = eq_df['equity'].resample('MS').last().ffill()
    monthly_returns = monthly_eq.pct_change() * 100
    plt.figure(figsize=(12, 4))
    plt.bar(monthly_returns.index, monthly_returns.values)
    plt.title(title)
    plt.ylabel('Monthly Return (%)')
    plt.xlabel('Month')
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def plot_signals_on_price(df, trades, out_path, price_col="close", title=None):
    """
    Line chart + entry/exit markers
    """
    plt.figure(figsize=(12, 5))
    plt.plot(df['date'], df[price_col], label="Price", color="blue")
    for t in trades:
        if t.get('entry_time') and t.get('exit_time'):
            plt.scatter(t['entry_time'], t['entry_price'], marker="^", color="green",
                        label="Entry" if t['direction'] == OrderPosition.LONG.name else "Short Entry")
            plt.scatter(t['exit_time'], t['exit_price'], marker="v", color="red",
                        label="Exit" if t['direction'] == OrderPosition.LONG.name else "Short Exit")
    plt.title(title or "Price with Entry/Exit Signals")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
