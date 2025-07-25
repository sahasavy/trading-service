import numpy as np

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Aroon(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Aroon
    """

    def __init__(self):
        super().__init__(IndicatorName.AROON.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        n = params.get('period', 14)
        aroon_up = df['high'].rolling(window=n + 1).apply(lambda x: float(np.argmax(x[::-1])) / n * 100, raw=True)
        aroon_down = df['low'].rolling(window=n + 1).apply(lambda x: float(np.argmin(x[::-1])) / n * 100, raw=True)
        df['AROON_UP'] = aroon_up
        df['AROON_DOWN'] = aroon_down
        df['AROON_LONG_SIGNAL'] = (aroon_up > 70).shift(1, fill_value=False).astype(int)
        df['AROON_SHORT_SIGNAL'] = (aroon_down > 70).shift(1, fill_value=False).astype(int)
