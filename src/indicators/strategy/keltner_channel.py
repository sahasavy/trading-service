from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Keltner(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Keltner Channel
    """

    def __init__(self):
        super().__init__(IndicatorName.KELTNER.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 20)
        atr_mult = params.get('multiplier', 2.0)
        ema = df['close'].ewm(span=period, adjust=False).mean()
        atr = df['high'].sub(df['low']).rolling(window=period).mean()
        upper = ema + atr_mult * atr
        lower = ema - atr_mult * atr
        cross_up = (df['close'] > upper)
        cross_down = (df['close'] < lower)
        df['KELTNER_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['KELTNER_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
