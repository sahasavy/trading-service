from src.indicators.base import Indicator


class Bollinger(Indicator):
    def __init__(self):
        super().__init__("BOLLINGER")

    def calculate(self, df, **params):
        if 'period' not in params or 'stddev' not in params:
            raise ValueError("BOLLINGER params 'period' and 'stddev' are required in indicator-config.yaml")
        period = params['period']
        stddev = params['stddev']
        df = df.copy()
        df['BOLL_MID'] = df['close'].rolling(window=period).mean()
        df['BOLL_UPPER'] = df['BOLL_MID'] + stddev * df['close'].rolling(window=period).std()
        df['BOLL_LOWER'] = df['BOLL_MID'] - stddev * df['close'].rolling(window=period).std()
        return df
