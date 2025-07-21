import pandas as pd

from src.indicators.base import Indicator


class ADX(Indicator):
    def __init__(self):
        super().__init__("ADX")

    def calculate(self, df, **params):
        if 'period' not in params or 'threshold' not in params or 'exit_threshold' not in params:
            raise ValueError(
                "ADX params 'period', 'threshold', and 'exit_threshold' are required in indicator-config.yaml")
        period = params['period']
        threshold = params['threshold']
        exit_threshold = params['exit_threshold']

        df = df.copy()
        high = df['high']
        low = df['low']
        close = df['close']
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr1 = abs(high - low)
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = abs(100 * (minus_dm.rolling(window=period).mean() / atr))
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        adx = dx.rolling(window=period).mean()
        df['ADX'] = adx
        df['ADX_SIGNAL'] = ((df['ADX'] > threshold) & (df['ADX'].shift(1) <= threshold)).astype(int)
        df['ADX_EXIT'] = ((df['ADX'] < exit_threshold) & (df['ADX'].shift(1) >= exit_threshold)).astype(int)
        return df
