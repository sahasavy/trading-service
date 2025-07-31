import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ADX(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> ADX
    """

    def __init__(self):
        super().__init__(IndicatorName.ADX.name)

    def compute_signals(self, df, params):
        if 'period' not in params or 'threshold' not in params or 'exit_threshold' not in params:
            raise ValueError(
                f"{self.name} params 'period', 'threshold', and 'exit_threshold' are required in backtest-config.yaml/indicator-config.yaml")

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
