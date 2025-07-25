from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Donchian(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Donchian Channel
    """

    def __init__(self):
        super().__init__(IndicatorName.DONCHIAN.name)

    def calculate(self, df, **params):
        if 'period' not in params:
            raise ValueError("DONCHIAN param 'period' is required in indicator-config.yaml")
        period = params['period']
        df = df.copy()
        df['DONCHIAN_UPPER'] = df['high'].rolling(window=period).max()
        df['DONCHIAN_LOWER'] = df['low'].rolling(window=period).min()
        return df

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 20)
        dc_high = df['high'].rolling(window=period).max()
        dc_low = df['low'].rolling(window=period).min()
        cross_up = (df['close'] > dc_high.shift(1))
        cross_down = (df['close'] < dc_low.shift(1))
        df['DONCHIAN_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['DONCHIAN_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
