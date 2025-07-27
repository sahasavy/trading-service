import os
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns

from src.commons.constants.constants import OrderPosition
from src.utils.backtest_util import construct_strategy_hyperparam_str


def add_visualizations(trading_symbol, interval, sim_dir, strategy_params, equity_curve, trades=None, price_df=None):
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

    # 5. Overlay Signals on Price Chart
    signals_path = os.path.join(plot_dir, f"{prefix}_signals_on_price.png")
    if price_df is not None and trades is not None:
        plot_signals_on_price(price_df, trades, out_path=signals_path,
                              title=f"Overlay Signals on Price Chart: {trading_symbol} {interval} {strategy_params['name']} - Signals")

    # 6. Histogram of returns
    hist_path = os.path.join(plot_dir, f"{prefix}_histogram_returns.png")
    plot_histogram_returns(equity_curve, save_path=hist_path,
                           title=f"Histogram of Daily Returns - {trading_symbol} {interval} {strategy_params['name']}")

    # 7. Rolling Sharpe
    rs_path = os.path.join(plot_dir, f"{prefix}_rolling_sharpe.png")
    plot_rolling_sharpe(equity_curve, save_path=rs_path,
                        title=f"Rolling Sharpe Ratio - {trading_symbol} {interval} {strategy_params['name']}")


def reconstruct_equity_curve(trades_df, initial_capital):
    trades_df = trades_df.sort_values('exit_time')
    eq = initial_capital
    curve = []
    for idx, t in trades_df.iterrows():
        eq += t['pnl']
        curve.append({'date': t['exit_time'], 'equity': eq})
    return curve


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
    Overlay Signals on Price Chart: Line chart + entry/exit markers
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    plt.figure(figsize=(12, 5))
    plt.plot(df['date'], df[price_col], label="Price", color="blue")
    for trade in trades:
        if trade.get('entry_time') and trade.get('exit_time'):
            plt.scatter(trade['entry_time'], trade['entry_price'], marker="^", color="green",
                        label="Entry" if trade['direction'] == OrderPosition.LONG.name else "Short Entry")
            plt.scatter(trade['exit_time'], trade['exit_price'], marker="v", color="red",
                        label="Exit" if trade['direction'] == OrderPosition.LONG.name else "Short Exit")
    plt.title(title or "Price with Entry/Exit Signals")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_histogram_returns(equity_curve, save_path=None, show=False, title='Histogram of Daily Returns (%)'):
    """
    Histogram Returns: Histogram plots help visualize the distribution of daily (or trade-by-trade) returns and
    are crucial for understanding the risk profile of a strategy.
    """
    eq_df = pd.DataFrame(equity_curve)
    eq_df['date'] = pd.to_datetime(eq_df['date'])
    eq_df.set_index('date', inplace=True)
    daily_eq = eq_df['equity'].resample('1D').last().ffill()
    daily_returns = daily_eq.pct_change() * 100
    plt.figure(figsize=(10, 5))
    plt.hist(daily_returns.dropna(), bins=50, color='purple', alpha=0.7)
    plt.title(title)
    plt.xlabel('Daily Return (%)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def plot_rolling_sharpe(equity_curve, window=30, save_path=None, show=False, title='Rolling Sharpe Ratio'):
    """
    Rolling Sharpe: A rolling Sharpe helps understand if the strategy’s risk-adjusted return is stable over time.
    """
    eq_df = pd.DataFrame(equity_curve)
    eq_df['date'] = pd.to_datetime(eq_df['date'])
    eq_df.set_index('date', inplace=True)
    daily_eq = eq_df['equity'].resample('1D').last().ffill()
    daily_returns = daily_eq.pct_change()
    rolling_sharpe = (daily_returns.rolling(window).mean() /
                      daily_returns.rolling(window).std()) * (252 ** 0.5)
    plt.figure(figsize=(12, 4))
    plt.plot(rolling_sharpe.index, rolling_sharpe.values, color='darkorange')
    plt.title(title + f" ({window} day window)")
    plt.xlabel('Date')
    plt.ylabel('Sharpe Ratio')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close()


def plot_heatmap_metrics(metrics_df, param_x, param_y, metric, save_path=None, title=None):
    """
    Heatmaps: Used for visualizing which hyperparameter combos perform best.

    param_x, param_y: column names of grid search params (e.g., 'fast', 'slow')
    metric: e.g., 'total_return', 'sharpe'
    """
    heatmap_df = metrics_df.pivot(index=param_y, columns=param_x, values=metric)
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap='YlGnBu')
    plt.title(title or f"{metric} by {param_x} and {param_y}")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.close()


def plot_candlestick_with_signals(df, trades, out_path, title=None):
    df_plot = df.copy()
    df_plot.set_index('date', inplace=True)
    ohlc_cols = ['open', 'high', 'low', 'close', 'volume']
    df_plot = df_plot[ohlc_cols]

    # Markers for entry/exit
    apds = []
    entries = [(t['entry_time'], t['entry_price']) for t in trades if t.get('entry_time')]
    exits = [(t['exit_time'], t['exit_price']) for t in trades if t.get('exit_time')]
    if entries:
        entry_times, entry_prices = zip(*entries)
        apds.append(
            mpf.make_addplot(pd.Series(entry_prices, index=entry_times), type='scatter', markersize=100, marker='^',
                             color='g'))
    if exits:
        exit_times, exit_prices = zip(*exits)
        apds.append(
            mpf.make_addplot(pd.Series(exit_prices, index=exit_times), type='scatter', markersize=100, marker='v',
                             color='r'))

    mpf.plot(df_plot, type='candle', addplot=apds, style='charles', title=title or 'Candlestick with Signals',
             savefig=out_path)


def plot_interactive_equity_curve(equity_curve, save_path=None, title="Equity Curve"):
    eq_df = pd.DataFrame(equity_curve)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=eq_df['date'], y=eq_df['equity'],
        mode='lines', name='Equity'
    ))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Equity')
    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()


def plot_top_n_runs(metrics_df, equity_curves_dict, metric="sharpe", n=3, sim_dir=""):
    top_n = metrics_df.sort_values(by=metric, ascending=False).head(n)
    plt.figure(figsize=(12, 6))
    for _, strategy_params in top_n.iterrows():
        hyperparam_str = construct_strategy_hyperparam_str(strategy_params)
        prefix = f"{strategy_params['token']}_{strategy_params['interval']}_{strategy_params['strategy']}_{hyperparam_str}"
        eq_curve = equity_curves_dict[prefix]
        plt.plot([x['date'] for x in eq_curve], [x['equity'] for x in eq_curve], label=prefix)
    plt.legend()
    plt.title(f"Top {n} Runs by {metric}")
    plt.tight_layout()
    plt.savefig(os.path.join(sim_dir, f"top_{n}_runs_{metric}.png"))
    plt.close()


def plot_overlay_strategies(equity_curves_dict, keys, save_path, title="Overlay Strategies Equity Curves"):
    plt.figure(figsize=(12, 6))
    for key in keys:
        eq_curve = equity_curves_dict[key]
        plt.plot([x['date'] for x in eq_curve], [x['equity'] for x in eq_curve], label=key)
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
