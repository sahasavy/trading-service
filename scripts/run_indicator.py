import os

import pandas as pd
from src.indicators.runner import apply_indicators

FEATURE_DATA_DIR = "data/feature"

if __name__ == "__main__":
    df = pd.read_csv("data/historical/HDFCBANK_minute.csv")

    df = apply_indicators(df)

    os.makedirs(FEATURE_DATA_DIR, exist_ok=True)
    df.to_csv(f"{FEATURE_DATA_DIR}/HDFCBANK_minute_feat.csv", index=False)
