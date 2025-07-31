from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class TRIX(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> TRIX
    """

    def __init__(self):
        super().__init__(IndicatorName.TRIX.name)

    def compute_signals(self, df, params):
        period = params.get('period', 15)
        ema1 = df['close'].ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        ema3 = ema2.ewm(span=period, adjust=False).mean()
        trix = ema3.pct_change() * 100
        df['TRIX'] = trix
        df['TRIX_LONG_SIGNAL'] = (trix > 0).shift(1, fill_value=False).astype(int)
        df['TRIX_SHORT_SIGNAL'] = (trix < 0).shift(1, fill_value=False).astype(int)
