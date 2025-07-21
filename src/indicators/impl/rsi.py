import numpy as np
import pandas as pd

from src.indicators.base import Indicator


class RSI(Indicator):
    def __init__(self):
        super().__init__("RSI")

    def calculate(self, df, **params):
        if 'period' not in params:
            raise ValueError("RSI param 'period' is required in indicator-config.yaml")
        period = params['period']
        overbought = params.get('overbought', 70)
        oversold = params.get('oversold', 30)
        df = df.copy()
        delta = df['close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=period).mean()
        avg_loss = pd.Series(loss).rolling(window=period).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI_OB'] = overbought
        df['RSI_OS'] = oversold
        return df
