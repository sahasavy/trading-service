from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class HullMA(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Hull MA
    """

    def __init__(self):
        super().__init__(IndicatorName.HULL_MA.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 21)
        wma_half = df['close'].rolling(window=period // 2).mean()
        wma_full = df['close'].rolling(window=period).mean()
        hull = 2 * wma_half - wma_full
        hull_ma = hull.rolling(window=int(np.sqrt(period))).mean()
        df['HULL_MA'] = hull_ma
        cross_up = (df['close'] > hull_ma) & (df['close'].shift(1) <= hull_ma.shift(1))
        cross_down = (df['close'] < hull_ma) & (df['close'].shift(1) >= hull_ma.shift(1))
        df['HULL_MA_LONG_SIGNAL'] = cross_up.shift(1, fill_value=False).astype(int)
        df['HULL_MA_SHORT_SIGNAL'] = cross_down.shift(1, fill_value=False).astype(int)
