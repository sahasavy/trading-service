from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Bollinger(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Bollinger Bands
    """

    def __init__(self):
        super().__init__(IndicatorName.BOLLINGER.name)

    def compute_signals(self, df, params):
        if 'period' not in params or 'stddev' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'stddev' are required in backtest-config.yaml/indicator-config.yaml")

        period = params.get('period', 20)
        stddev = params.get('stddev', 2.0)

        ma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper = ma + (stddev * std)
        lower = ma - (stddev * std)
        cross_up = (df['close'] > upper) & (df['close'].shift(1) <= upper.shift(1))
        cross_down = (df['close'] < lower) & (df['close'].shift(1) >= lower.shift(1))

        df['BOLLINGER_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['BOLLINGER_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
