import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ADX(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> ADX
    """

    def __init__(self):
        super().__init__(IndicatorName.ADX.name)

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

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 14)
        threshold = params.get('threshold', 25)
        exit_threshold = params.get('exit_threshold', 20)

        high = df['high']
        low = df['low']
        close = df['close']
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).sum() / atr)
        minus_di = 100 * (abs(minus_dm.rolling(period).sum()) / atr)
        dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
        adx = dx.rolling(period).mean()
        df['ADX'] = adx
        df['ADX_LONG_SIGNAL'] = ((adx > threshold) & (plus_di > minus_di)).shift(1, fill_value=False).astype(int)
        df['ADX_SHORT_SIGNAL'] = ((adx > threshold) & (minus_di > plus_di)).shift(1, fill_value=False).astype(int)
