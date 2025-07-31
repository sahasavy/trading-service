from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ROC(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Rate of Change (ROC)
    """

    def __init__(self):
        super().__init__(IndicatorName.ROC.name)

    def compute_signals(self, df, params):
        period = params.get('period', 10)
        roc = df['close'].pct_change(periods=period) * 100
        threshold = params.get('threshold', 0)
        df['ROC'] = roc
        df['ROC_LONG_SIGNAL'] = (roc > threshold).shift(1, fill_value=False).astype(int)
        df['ROC_SHORT_SIGNAL'] = (roc < -threshold).shift(1, fill_value=False).astype(int)
