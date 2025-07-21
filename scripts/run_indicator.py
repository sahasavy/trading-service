import pandas as pd
from src.indicators.runner import apply_indicators

if __name__ == "__main__":
    df = pd.read_csv("data/historical/HDFCBANK_minute.csv")

    df = apply_indicators(df)

    df.to_csv("data/feature/HDFCBANK_minute_feat.csv", index=False)
