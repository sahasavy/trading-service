import numpy as np
from src.indicators.base import Indicator


class SuperTrend(Indicator):
    def __init__(self):
        super().__init__("SUPER_TREND")

    def calculate(self, df, **params):
        if 'period' not in params or 'multiplier' not in params:
            raise ValueError("SUPER_TREND params 'period' and 'multiplier' are required in indicator-config.yaml")
        period = params['period']
        multiplier = params['multiplier']
        df = df.copy()
        hl2 = (df['high'] + df['low']) / 2
        atr = (df['high'] - df['low']).rolling(window=period).mean()
        upperband = hl2 + (multiplier * atr)
        lowerband = hl2 - (multiplier * atr)
        supertrend = np.full(len(df), np.nan)
        for i in range(period, len(df)):
            if i == period:
                supertrend[i] = upperband[i]
            else:
                prev_close = df['close'].iloc[i - 1]
                if prev_close > supertrend[i - 1]:
                    supertrend[i] = lowerband[i] if lowerband[i] > supertrend[i - 1] else supertrend[i - 1]
                else:
                    supertrend[i] = upperband[i] if upperband[i] < supertrend[i - 1] else supertrend[i - 1]
        df['SUPER_TREND'] = supertrend
        return df
