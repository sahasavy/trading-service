import numpy as np
import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class MFI(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Money Flow Index (MFI)
    """

    def __init__(self):
        super().__init__(IndicatorName.MFI.name)

    def compute_signals(self, df, params):
        period = params.get('period', 14)
        tp = (df['high'] + df['low'] + df['close']) / 3
        mf = tp * df['volume']
        pos_mf = np.where(tp > tp.shift(1), mf, 0)
        neg_mf = np.where(tp < tp.shift(1), mf, 0)
        mfr = pd.Series(pos_mf).rolling(period).sum() / pd.Series(neg_mf).rolling(period).sum()
        mfi = 100 - 100 / (1 + mfr)
        df['MFI'] = mfi
        df['MFI_LONG_SIGNAL'] = (mfi < 20).shift(1, fill_value=False).astype(int)
        df['MFI_SHORT_SIGNAL'] = (mfi > 80).shift(1, fill_value=False).astype(int)
