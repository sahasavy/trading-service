import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ATR(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> ATR (Average True Range)
    """

    def __init__(self):
        super().__init__(IndicatorName.ATR.name)

    def compute_signals(self, df, params):
        period = params.get('period', 14)

        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - df['close'].shift()).abs()
        tr3 = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        df['ATR'] = tr.rolling(window=period).mean()
        # ATR is not strictly a signal, so no _LONG_SIGNAL/_SHORT_SIGNAL unless custom
