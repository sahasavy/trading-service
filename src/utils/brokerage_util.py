from src.commons.constants.constants import OrderSide, Exchange, Segment
from src.utils.file_util import read_config

BROKERAGE_CFG = "config/brokerage-config.yml"


def calculate_brokerage(segment, side, price, qty, exchange):
    brokerage_cfg = read_config(BROKERAGE_CFG)
    seg = brokerage_cfg['segments'][segment]
    turnover = price * qty

    # Brokerage
    if segment == Segment.FNO_OPTION.name:
        raw_brokerage = seg['brokerage_cap']
    else:
        raw_brokerage = turnover * seg['brokerage_percent']
        raw_brokerage = min(raw_brokerage, seg['brokerage_cap'])

    # STT
    stt = 0
    if side == OrderSide.BUY.name:
        stt = turnover * seg.get('stt_percent_buy', 0)
    else:
        stt = turnover * seg.get('stt_percent_sell', 0)

    # Transaction charges
    txn_pct = seg[f"txn_percent_nse"] if exchange.upper() == Exchange.NSE.name else seg[f"txn_percent_bse"]
    txn = turnover * txn_pct

    # SEBI
    sebi = turnover * brokerage_cfg['gst_percent']

    # Stamp duty only on BUY
    stamp = turnover * seg['stamp_percent_buy'] if side == OrderSide.BUY.name else 0

    # SEBI charges per crore
    sebi = turnover * (seg['sebi_per_crore'] / 1e7)

    # GST on (brokerage + txn + sebi)
    gst = (raw_brokerage + txn + sebi) * brokerage_cfg['gst_percent']

    total = raw_brokerage + stt + txn + sebi + stamp + gst
    return dict(
        brokerage=round(raw_brokerage, 2),
        stt=round(stt, 2),
        txn=round(txn, 2),
        sebi=round(sebi, 2),
        stamp=round(stamp, 2),
        gst=round(gst, 2),
        total=round(total, 2)
    )


# TODO - Will remove everything from below when backtest simulation is ready
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--segment", required=True)
    parser.add_argument("--side", choices=["BUY", "SELL"], required=True)
    parser.add_argument("--price", type=float, required=True)
    parser.add_argument("--qty", type=int, required=True)
    parser.add_argument("--exchange", choices=["NSE", "BSE"], required=True)
    args = parser.parse_args()

    result = calculate_brokerage(args.segment, args.side, args.price, args.qty, args.exchange)
    print(f"📊 {args.segment} | {args.side} | Turnover ₹{args.price * args.qty}")
    for k, v in result.items():
        print(f"- {k.upper():<8}: ₹{v}")
    print(f"✅ Total Charges: ₹{result['total']}")

# python3 src/utils/brokerage_util.py --segment EQUITY_INTRADAY --side SELL --price 1000 --qty 100 --exchange NSE
