import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class StochRSI(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Stochastic RSI
    """

    def __init__(self):
        super().__init__(IndicatorName.STOCH_RSI.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        n = params.get('period', 14)
        rsi = df['close'].rolling(window=n).apply(lambda x: pd.Series(x).pct_change().mean())
        min_rsi = rsi.rolling(window=n).min()
        max_rsi = rsi.rolling(window=n).max()
        stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
        df['STOCH_RSI'] = stoch_rsi
        df['STOCH_RSI_LONG_SIGNAL'] = (stoch_rsi < 0.2).shift(1, fill_value=False).astype(int)
        df['STOCH_RSI_SHORT_SIGNAL'] = (stoch_rsi > 0.8).shift(1, fill_value=False).astype(int)
