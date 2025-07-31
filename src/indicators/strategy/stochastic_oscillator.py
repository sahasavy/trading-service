from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Stochastic(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Stochastic Oscillator
    """

    def __init__(self):
        super().__init__(IndicatorName.STOCHASTIC.name)

    def compute_signals(self, df, params):
        k_period = params.get('k_period', 14)
        d_period = params.get('d_period', 3)
        overbought = params.get('overbought', 80)
        oversold = params.get('oversold', 20)

        high_roll = df['high'].rolling(window=k_period).max()
        low_roll = df['low'].rolling(window=k_period).min()
        k = 100 * ((df['close'] - low_roll) / (high_roll - low_roll))
        d = k.rolling(window=d_period).mean()

        df['STOCH_K'] = k
        df['STOCH_D'] = d
        df['STOCHASTIC_LONG_SIGNAL'] = (k < oversold).shift(1, fill_value=False).astype(int)
        df['STOCHASTIC_SHORT_SIGNAL'] = (k > overbought).shift(1, fill_value=False).astype(int)
