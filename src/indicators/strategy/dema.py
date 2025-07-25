from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class DEMA(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> DEMA (Double EMA)
    """

    def __init__(self):
        super().__init__(IndicatorName.DEMA.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 21)
        ema1 = df['close'].ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        dema = 2 * ema1 - ema2
        df['DEMA'] = dema
        cross_up = (df['close'] > dema) & (df['close'].shift(1) <= dema.shift(1))
        cross_down = (df['close'] < dema) & (df['close'].shift(1) >= dema.shift(1))
        df['DEMA_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['DEMA_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
