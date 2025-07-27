from src.commons.constants.constants import TradeEvent
from src.utils.backtest_util import construct_strategy_hyperparam_str


def log_backtest_run_header(trading_symbol, interval, params):
    hyperparam_str = construct_strategy_hyperparam_str(params)
    print(f"\n========== Backtest: {trading_symbol} {interval} {params['name']} {hyperparam_str} ==========")


def log_backtest_trade(event, trade, idx):
    # Print ENTRY/EXIT, with all params if present in trade
    pass
    # if event == TradeEvent.ENTRY.name:
    #     print(
    #         f"🟢 [{trade['direction']}] Entry idx {idx} | {trade['entry_time']} @ {trade['entry_price']:.2f} | Qty={trade['qty']}")
    # else:
    #     print(
    #         f"🔴 [{trade['direction']}] Exit idx {idx} | {trade['exit_time']} @ {trade['exit_price']:.2f} | P&L={trade['pnl']:.2f} | Reason: {trade['exit_reason']}")


def log_backtest_metrics(metrics, trading_symbol, interval, params, split):
    hyperparam_str = construct_strategy_hyperparam_str(params)
    print(f"\n📊 {trading_symbol} {interval} {params['name']} {hyperparam_str} [{split}] Results:")
    print(
        f"  Total Return: {metrics['total_return']:.2f}%   CAGR: {metrics['cagr']:.2f}%   Calmar: {metrics['calmar']:.2f}")
    print(
        f"  Sharpe: {metrics['sharpe']:.2f}  Sortino: {metrics['sortino']:.2f}   Volatility: {metrics['volatility']:.2f}%")
    print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%   Win Rate: {metrics['win_rate']:.2f}%")
    print(
        f"  Profit Factor: {metrics['profit_factor']:.2f}   Best/Worst: {metrics['best_trade']:.2f} / {metrics['worst_trade']:.2f}")
    print(f"  Median Trade: {metrics['median_trade']:.2f}  Expectancy: {metrics['expectancy']:.2f}")
    print(f"  Avg/Mdn Holding (min): {metrics['avg_holding']:.2f} / {metrics['median_holding']:.2f}")
    print(f"  Max Win Streak: {metrics['max_win_streak']}   Max Loss Streak: {metrics['max_loss_streak']}")
    print(f"  Trades: {metrics['trades']}   Exposure: {metrics['exposure']:.2f}%")
    print(f"  Monthly returns: {metrics['monthly_returns']}")
