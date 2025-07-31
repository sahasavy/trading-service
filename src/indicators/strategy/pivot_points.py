from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Pivot(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Pivot Points
    """

    def __init__(self):
        super().__init__(IndicatorName.PIVOT.name)

    def compute_signals(self, df, params):
        pivot = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3
        df['PIVOT'] = pivot
        df['PIVOT_LONG_SIGNAL'] = (df['close'] > pivot).shift(1, fill_value=False).astype(int)
        df['PIVOT_SHORT_SIGNAL'] = (df['close'] < pivot).shift(1, fill_value=False).astype(int)
