from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Envelope(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Envelope
    """

    def __init__(self):
        super().__init__(IndicatorName.ENVELOPE.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 20)
        pct = params.get('percent', 0.025)
        ma = df['close'].rolling(window=period).mean()
        upper = ma * (1 + pct)
        lower = ma * (1 - pct)
        cross_up = (df['close'] > upper)
        cross_down = (df['close'] < lower)
        df['ENVELOPE_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['ENVELOPE_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
