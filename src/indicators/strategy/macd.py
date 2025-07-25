from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class MACD(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> MACD
    """

    def __init__(self):
        super().__init__(IndicatorName.MACD.name)

    def calculate(self, df, **params):
        if 'fast' not in params or 'slow' not in params or 'signal' not in params:
            raise ValueError("MACD params 'fast', 'slow', and 'signal' are required in indicator-config.yaml")
        fast = params['fast']
        slow = params['slow']
        signal = params['signal']
        df = df.copy()
        df['MACD_FAST'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['MACD_SLOW'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['MACD_LINE'] = df['MACD_FAST'] - df['MACD_SLOW']
        df['MACD_SIGNAL'] = df['MACD_LINE'].ewm(span=signal, adjust=False).mean()
        df['MACD_HIST'] = df['MACD_LINE'] - df['MACD_SIGNAL']
        return df

    @staticmethod
    def compute_signals(df, params):
        fast = params.get('fast', 12)
        slow = params.get('slow', 26)
        signal = params.get('signal', 9)
        df['EMA_FAST'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['EMA_SLOW'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['MACD'] = df['EMA_FAST'] - df['EMA_SLOW']
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        cross_up = (df['MACD'] > df['MACD_SIGNAL']) & (df['MACD'].shift(1) <= df['MACD_SIGNAL'].shift(1))
        cross_down = (df['MACD'] < df['MACD_SIGNAL']) & (df['MACD'].shift(1) >= df['MACD_SIGNAL'].shift(1))
        df['MACD_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['MACD_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
