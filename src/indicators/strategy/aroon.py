import numpy as np

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Aroon(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Aroon
    """

    def __init__(self):
        super().__init__(IndicatorName.AROON.name)

    def compute_signals(self, df, params):
        period = params.get('period', 14)

        aroon_up = df['high'].rolling(window=period + 1).apply(lambda x: float(np.argmax(x[::-1])) / period * 100,
                                                               raw=True)
        aroon_down = df['low'].rolling(window=period + 1).apply(lambda x: float(np.argmin(x[::-1])) / period * 100,
                                                                raw=True)
        df['AROON_UP'] = aroon_up
        df['AROON_DOWN'] = aroon_down
        df['AROON_LONG_SIGNAL'] = (aroon_up > 70).shift(1, fill_value=False).astype(int)
        df['AROON_SHORT_SIGNAL'] = (aroon_down > 70).shift(1, fill_value=False).astype(int)
