from src.indicators.base import Indicator


class EMACross(Indicator):
    def __init__(self):
        super().__init__("EMA_CROSS")

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
