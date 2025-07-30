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
    #         f"🔴 [{trade['direction']}] Exit idx {idx} | {trade['exit_time']} @ {trade['exit_price']:.2f} | "
    #         f"P&L={trade.get('pnl', 0):.2f} | GrossPnL={trade.get('gross_pnl', 0):.2f} | "
    #         f"Fee(Buy/Sell): {trade.get('fee_buy', 0):.2f}/{trade.get('fee_sell', 0):.2f} | "
    #         f"Total Fee: {trade.get('total_fee', 0):.2f} | Reason: {trade['exit_reason']}"
    #     )


def log_backtest_metrics(metrics, trading_symbol, interval, params, split):
    hyperparam_str = construct_strategy_hyperparam_str(params)
    print(f"\n📊 {trading_symbol} {interval} {params['name']} {hyperparam_str} [{split}] Results:")

    print("----- PnL & Fees -----")
    print(
        f"  Gross PnL: {metrics['gross_pnl']:.2f}    "
        f"Total Fees: {metrics['total_fees']:.2f}    "
        f"Net PnL: {metrics['net_pnl']:.2f}    "
        f"Equity Final: {metrics['equity_final']:.2f}"
    )
    print(
        f"  Total Return: {metrics['total_return']:.2f}%   "
        f"CAGR: {metrics['cagr']:.2f}%   "
        f"Calmar: {metrics['calmar']:.2f}"
    )

    print("----- Risk & Return -----")
    print(
        f"  Sharpe: {metrics['sharpe']:.2f}   Sortino: {metrics['sortino']:.2f}   Volatility: {metrics['volatility']:.2f}%"
    )
    print(
        f"  Max Drawdown: {metrics['max_drawdown']:.2f}%"
    )

    print("----- Trade Stats -----")
    print(
        f"  Win Rate: {metrics['win_rate']:.2f}%   "
        f"Profit Factor: {metrics['profit_factor']:.2f}   "
        f"Best/Worst: {metrics['best_trade']:.2f} / {metrics['worst_trade']:.2f}"
    )
    print(
        f"  Median Trade: {metrics['median_trade']:.2f}   "
        f"Expectancy: {metrics['expectancy']:.2f}"
    )
    print(
        f"  Avg/Mdn Holding (min): {metrics['avg_holding']:.2f} / {metrics['median_holding']:.2f}"
    )
    print(
        f"  Max Win Streak: {metrics['max_win_streak']}   "
        f"Max Loss Streak: {metrics['max_loss_streak']}"
    )
    print(
        f"  Trades: {metrics['trades']}   "
        f"Exposure: {metrics['exposure']:.2f}%"
    )

    print("----- Monthly Returns -----")
    print(f"  Monthly returns: {metrics['monthly_returns']}")
