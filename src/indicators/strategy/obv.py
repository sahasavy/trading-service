import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class OBV(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> On-Balance Volume (OBV)
    """

    def __init__(self):
        super().__init__(IndicatorName.OBV.name)

    def calculate(self, df, **params):
        # TODO - Add logic
        pass

    @staticmethod
    def compute_signals(df, params):
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i - 1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        df['OBV'] = obv
        df['OBV_LONG_SIGNAL'] = (df['OBV'] > pd.Series(obv).rolling(20).mean()).shift(1, fill_value=False).astype(int)
        df['OBV_SHORT_SIGNAL'] = (df['OBV'] < pd.Series(obv).rolling(20).mean()).shift(1, fill_value=False).astype(int)
