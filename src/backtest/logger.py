from src.commons.constants.constants import TradeEvent
from src.utils.file_util import construct_strategy_hyperparam_str


def log_run_header(token, interval, params):
    pstr = construct_strategy_hyperparam_str(params)
    print(f"\n\n========== Backtest: {token} {interval} {params['name']} {pstr} ==========")


def log_trade(event, trade, idx):
    # Print ENTRY/EXIT, with all params if present in trade
    if event == TradeEvent.ENTRY.name:
        print(
            f"🟢 [{trade['direction']}] Entry idx {idx} | {trade['entry_time']} @ {trade['entry_price']:.2f} | Qty={trade['qty']}")
    else:
        print(
            f"🔴 [{trade['direction']}] Exit idx {idx} | {trade['exit_time']} @ {trade['exit_price']:.2f} | P&L={trade['pnl']:.2f} | Reason: {trade['exit_reason']}")


def log_metrics(metrics, token, interval, params, split):
    pstr = construct_strategy_hyperparam_str(params)
    print(f"\n📊 {token} {interval} {params['name']} {pstr} [{split}] Results:")
    print(f"  Total Return: {metrics['total_return']:.2f}%   CAGR: {metrics['cagr']:.2f}%")
    print(f"  Volatility: {metrics['volatility']:.2f}%   Sharpe Ratio: {metrics['sharpe']:.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"  Win Rate: {metrics['win_rate']:.2f}%  |  Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"  Trades: {metrics['trades']}   |   Exposure: {metrics['exposure']:.2f}%")
