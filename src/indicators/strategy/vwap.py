from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class VWAP(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> VWAP
    """

    def __init__(self):
        super().__init__(IndicatorName.VWAP.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        cum_vol = df['volume'].cumsum()
        cum_vp = (df['close'] * df['volume']).cumsum()
        vwap = cum_vp / cum_vol
        df['VWAP'] = vwap
        cross_up = (df['close'] > vwap)
        cross_down = (df['close'] < vwap)
        df['VWAP_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['VWAP_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
