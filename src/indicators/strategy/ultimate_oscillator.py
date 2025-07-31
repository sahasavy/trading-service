import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class UltimateOsc(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Ultimate Oscillator
    """

    def __init__(self):
        super().__init__(IndicatorName.ULTIMATE_OSC.name)

    def compute_signals(self, df, params):
        # TODO - See documentation for full details
        high, low, close = df['high'], df['low'], df['close']
        bp = close - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
        tr = pd.concat([high, close.shift(1)], axis=1).max(axis=1) - pd.concat([low, close.shift(1)], axis=1).min(
            axis=1)
        avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
        avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
        avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
        uo = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7
        df['ULTIMATE_OSC'] = uo
        df['ULTIMATE_OSC_LONG_SIGNAL'] = (uo > 70).shift(1, fill_value=False).astype(int)
        df['ULTIMATE_OSC_SHORT_SIGNAL'] = (uo < 30).shift(1, fill_value=False).astype(int)
