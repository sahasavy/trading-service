from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Donchian(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Donchian Channel
    """

    def __init__(self):
        super().__init__(IndicatorName.DONCHIAN.name)

    def compute_signals(self, df, params):
        if 'period' not in params:
            raise ValueError(f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml")

        period = params.get('period', 20)
        dc_high = df['high'].rolling(window=period).max()
        dc_low = df['low'].rolling(window=period).min()

        cross_up = (df['close'] > dc_high.shift(1))
        cross_down = (df['close'] < dc_low.shift(1))

        df['DONCHIAN_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['DONCHIAN_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
