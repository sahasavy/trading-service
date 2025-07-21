from src.indicators.base import Indicator


class SMACross(Indicator):
    def __init__(self):
        super().__init__("SMA_CROSS")

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
