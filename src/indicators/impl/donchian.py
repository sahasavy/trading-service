from src.indicators.base import Indicator


class Donchian(Indicator):
    def __init__(self):
        super().__init__("DONCHIAN")

    def calculate(self, df, **params):
        if 'period' not in params:
            raise ValueError("DONCHIAN param 'period' is required in indicator-config.yaml")
        period = params['period']
        df = df.copy()
        df['DONCHIAN_UPPER'] = df['high'].rolling(window=period).max()
        df['DONCHIAN_LOWER'] = df['low'].rolling(window=period).min()
        return df
