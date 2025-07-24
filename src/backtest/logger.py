from src.commons.constants.constants import TradeEvent


def log_run_header(token, interval, fast, slow):
    print(f"\n\n========== Backtest: {token} {interval} EMA({fast},{slow}) ==========")


def log_trade(event, trade, idx):
    if event == TradeEvent.ENTRY.name:
        print(
            f"🟢 [{trade['direction']}] Entry idx {idx} | {trade['entry_time']} @ {trade['entry_price']:.2f} | Qty={trade['qty']}")
    else:
        print(
            f"🔴 [{trade['direction']}] Exit idx {idx} | {trade['exit_time']} @ {trade['exit_price']:.2f} | P&L={trade['pnl']:.2f} | Reason: {trade['exit_reason']}")


def log_metrics(metrics, token, interval, fast, slow, split):
    print(f"\n📊 {token} {interval} EMA({fast},{slow}) [{split}] Results:")
    print(f"  Total Return: {metrics['total_return']:.2f}%   CAGR: {metrics['cagr']:.2f}%")
    print(f"  Volatility: {metrics['volatility']:.2f}%   Sharpe Ratio: {metrics['sharpe']:.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"  Win Rate: {metrics['win_rate']:.2f}%  |  Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"  Trades: {metrics['trades']}   |   Exposure: {metrics['exposure']:.2f}%")
