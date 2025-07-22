import yaml

BROKERAGE_CFG = "config/brokerage-config.yml"


def load_brokerage_config():
    with open(BROKERAGE_CFG) as f:
        return yaml.safe_load(f)


def calculate_brokerage(segment, side, price, qty, exchange):
    cfg = load_brokerage_config()
    seg = cfg['segments'][segment]
    turnover = price * qty

    # Brokerage
    if segment == "FNO_OPTION":
        raw_brokerage = seg['brokerage_cap']
    else:
        raw_brokerage = turnover * seg['brokerage_percent']
        raw_brokerage = min(raw_brokerage, seg['brokerage_cap'])

    # STT
    stt = 0
    if side == "BUY":
        stt = turnover * seg.get('stt_percent_buy', 0)
    else:
        stt = turnover * seg.get('stt_percent_sell', 0)

    # Transaction charges
    txn_pct = seg[f"txn_percent_nse"] if exchange.upper() == "NSE" else seg[f"txn_percent_bse"]
    txn = turnover * txn_pct

    # SEBI
    sebi = turnover * cfg['gst_percent']  # Fix below

    # Stamp duty only on BUY
    stamp = turnover * seg['stamp_percent_buy'] if side == "BUY" else 0

    # SEBI charges per crore
    sebi = turnover * (seg['sebi_per_crore'] / 1e7)

    # GST on (brokerage + txn + sebi)
    gst = (raw_brokerage + txn + sebi) * cfg['gst_percent']

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

# python3 src/utils/brokerage.py --segment EQUITY_INTRADAY --side SELL --price 1000 --qty 100 --exchange NSE
