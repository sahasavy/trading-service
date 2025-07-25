from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class SMACross(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> SMA CROSS
    """

    def __init__(self):
        super().__init__(IndicatorName.SMA_CROSS.name)

    def calculate(self, df, **params):
        if 'fast' not in params or 'slow' not in params:
            raise ValueError("SMA_CROSS params 'fast' and 'slow' are required in indicator-config.yaml")
        fast = params['fast']
        slow = params['slow']
        df = df.copy()
        df['SMA_FAST'] = df['close'].rolling(window=fast).mean()
        df['SMA_SLOW'] = df['close'].rolling(window=slow).mean()
        df['SMA_CROSS_SIGNAL'] = (df['SMA_FAST'] > df['SMA_SLOW']).astype(int)
        return df

    @staticmethod
    def compute_signals(df, params):
        if 'fast' not in params or 'slow' not in params:
            raise ValueError("SMA_CROSS params 'fast' and 'slow' are required in backtest-config.yaml")
        fast = params['fast']
        slow = params['slow']
        df['SMA_FAST'] = df['close'].rolling(window=fast, min_periods=fast).mean()
        df['SMA_SLOW'] = df['close'].rolling(window=slow, min_periods=slow).mean()
        cross_up = (df['SMA_FAST'] > df['SMA_SLOW']) & (df['SMA_FAST'].shift(1) <= df['SMA_SLOW'].shift(1))
        cross_down = (df['SMA_FAST'] < df['SMA_SLOW']) & (df['SMA_FAST'].shift(1) >= df['SMA_SLOW'].shift(1))
        df['SMA_CROSS_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['SMA_CROSS_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
