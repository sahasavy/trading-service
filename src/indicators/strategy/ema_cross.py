from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class EMACross(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> EMA CROSS
    """

    def __init__(self):
        super().__init__(IndicatorName.EMA_CROSS.name)

    def calculate(self, df, **params):
        if 'fast' not in params or 'slow' not in params:
            raise ValueError("EMA_CROSS params 'fast' and 'slow' are required in indicator-config.yaml")
        fast = params['fast']
        slow = params['slow']
        df = df.copy()
        df['EMA_FAST'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['EMA_SLOW'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['EMA_CROSS_SIGNAL'] = (df['EMA_FAST'] > df['EMA_SLOW']).astype(int)
        return df

    @staticmethod
    def compute_signals(df, params):
        """
        Adds lookahead-safe EMA cross signals to df:
          - 'EMA_FAST'
          - 'EMA_SLOW'
          - 'EMA_CROSS_LONG_SIGNAL': 1 if previous bar fast crossed above slow (bullish), else 0
          - 'EMA_CROSS_SHORT_SIGNAL': 1 if previous bar fast crossed below slow (bearish), else 0
        """
        if 'fast' not in params or 'slow' not in params:
            raise ValueError("EMA_CROSS params 'fast' and 'slow' are required in backtest-config.yaml")
        fast = params['fast']
        slow = params['slow']
        df['EMA_FAST'] = df['close'].ewm(span=fast, adjust=False, min_periods=fast).mean()
        df['EMA_SLOW'] = df['close'].ewm(span=slow, adjust=False, min_periods=slow).mean()
        # Detect crossovers only, not just above/below
        cross_up = ((df['EMA_FAST'] > df['EMA_SLOW']) &
                    (df['EMA_FAST'].shift(1) <= df['EMA_SLOW'].shift(1)))
        cross_down = ((df['EMA_FAST'] < df['EMA_SLOW']) &
                      (df['EMA_FAST'].shift(1) >= df['EMA_SLOW'].shift(1)))
        # Shift by 1 bar for lookahead safety
        df['EMA_CROSS_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['EMA_CROSS_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
