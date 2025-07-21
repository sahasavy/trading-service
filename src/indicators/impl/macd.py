from src.indicators.base import Indicator


class MACD(Indicator):
    def __init__(self):
        super().__init__("MACD")

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
