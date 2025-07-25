from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Pivot(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Pivot Points
    """

    def __init__(self):
        super().__init__(IndicatorName.PIVOT.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        pivot = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
        df['PIVOT'] = pivot
        df['PIVOT_LONG_SIGNAL'] = (df['close'] > pivot).shift(1, fill_value=False).astype(int)
        df['PIVOT_SHORT_SIGNAL'] = (df['close'] < pivot).shift(1, fill_value=False).astype(int)
