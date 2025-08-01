import glob
import os

from src.utils.backtest_util import construct_strategy_hyperparam_str
from src.utils.file_util import read_df_from_csv
from src.utils.visualization_util import (
    plot_heatmap_metrics,
    plot_top_n_runs,
    plot_overlay_strategies
)


def find_latest_sim_dir(base_dir="data/simulation_results"):
    sim_dirs = sorted([d for d in os.listdir(base_dir) if d.startswith("sim_")],
                      key=lambda x: int(x.split('_')[1]))
    if not sim_dirs:
        raise FileNotFoundError("No simulation result directories found!")
    return os.path.join(base_dir, sim_dirs[-1])


def load_equity_curves(trade_dir):
    curves = {}
    for trade_file in glob.glob(os.path.join(trade_dir, "*.csv")):
        df = read_df_from_csv(trade_file, parse_dates=['entry_time', 'exit_time'])
        # TODO - Try to also load corresponding equity curve if you saved it separately (or reconstruct from trade log)
        # For now, let's skip and just use trade info for plotting signals
        curves[os.path.splitext(os.path.basename(trade_file))[0]] = df
    return curves


def main():
    sim_dir = find_latest_sim_dir()
    print(f"🕵️ Analyzing: {sim_dir}")

    metrics_path = os.path.join(sim_dir, "metrics_summary.csv")
    metrics_df = read_df_from_csv(metrics_path)

    trade_dir = os.path.join(sim_dir, "trade")
    plot_dir = os.path.join(sim_dir, "plots")
    os.makedirs(plot_dir, exist_ok=True)

    # ----- 1. Heatmap for a strategy -----
    for strat in metrics_df['strategy'].unique():
        df = metrics_df[metrics_df['strategy'] == strat]
        param_cols = [col for col in df.columns if
                      col.endswith('fast') or col.endswith('period') or col.endswith('slow')]
        if len(param_cols) >= 2:
            x, y = param_cols[0], param_cols[1]
            plot_heatmap_metrics(df, param_x=x, param_y=y, metric="total_return",
                                 save_path=os.path.join(plot_dir, f"heatmap_{strat}_total_return.png"),
                                 title=f"Total Return Heatmap - {strat}")

    # ----- 2. Top-N runs (by Sharpe) -----
    N = 3
    plot_top_n_runs(metrics_df, metric="sharpe", n=N, sim_dir=sim_dir)

    # ----- 3. Overlay strategies -----
    # You can overlay all runs for a token/interval, or different strategies for a token
    for token in metrics_df['token'].unique():
        for interval in metrics_df['interval'].unique():
            subset = metrics_df[(metrics_df['token'] == token) & (metrics_df['interval'] == interval)]
            if subset.empty:
                continue
            keys = []
            equity_curves_dict = {}
            for _, row in subset.iterrows():
                key = f"{row['token']}_{row['interval']}_{row['strategy']}_{construct_strategy_hyperparam_str(row)}"
                trade_file = os.path.join(trade_dir, key + ".csv")
                if os.path.exists(trade_file):
                    df_trades = read_df_from_csv(trade_file, parse_dates=['entry_time', 'exit_time'])
                    equity_curve = []  # TODO: Load/recompute actual equity curve if saved
                    # TODO - Placeholder: simulate as equity = initial_capital + cumsum(pnl)
                    eq = row.get('initial_capital', 1000000)
                    for idx, t in df_trades.iterrows():
                        eq += t['pnl']
                        equity_curve.append({'date': t['exit_time'], 'equity': eq})
                    equity_curves_dict[key] = equity_curve
                    keys.append(key)
            if equity_curves_dict:
                save_path = os.path.join(plot_dir, f"{token}_{interval}_overlay_equity.png")
                plot_overlay_strategies(equity_curves_dict, keys, save_path,
                                        title=f"{token} {interval} Equity Curves Overlay")

    # ----- 4. Example: Single run deep-dive -----
    best_row = metrics_df.sort_values('sharpe', ascending=False).iloc[0]
    key = f"{best_row['token']}_{best_row['interval']}_{best_row['strategy']}_{construct_strategy_hyperparam_str(best_row)}"
    trade_file = os.path.join(trade_dir, key + ".csv")
    if os.path.exists(trade_file):
        trades = read_df_from_csv(trade_file, parse_dates=['entry_time', 'exit_time'])
        # TODO - If you saved the full price dataframe (with signals), you could plot signals
        # For now, you could skip or use last backtest's df for demo
        # Example:
        # plot_signals_on_price(price_df, trades, out_path=...)
        # plot_candlestick_with_signals(price_df, trades, out_path=...)
        pass

    print("✅ Analytics visualizations complete!")


if __name__ == "__main__":
    main()
