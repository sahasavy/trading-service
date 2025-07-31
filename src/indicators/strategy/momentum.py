from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Momentum(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Momentum
    """

    def __init__(self):
        super().__init__(IndicatorName.MOMENTUM.name)

    def compute_signals(self, df, params):
        period = params.get('period', 10)
        momentum = df['close'].diff(period)
        df['MOMENTUM'] = momentum
        df['MOMENTUM_LONG_SIGNAL'] = (momentum > 0).shift(1, fill_value=False).astype(int)
        df['MOMENTUM_SHORT_SIGNAL'] = (momentum < 0).shift(1, fill_value=False).astype(int)
