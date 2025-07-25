import numpy as np
import pandas as pd

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class RSI(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> RSI
    """

    def __init__(self):
        super().__init__(IndicatorName.RSI.name)

    def calculate(self, df, **params):
        if 'period' not in params:
            raise ValueError("RSI param 'period' is required in indicator-config.yaml")
        period = params['period']
        overbought = params.get('overbought', 70)
        oversold = params.get('oversold', 30)
        df = df.copy()
        delta = df['close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=period).mean()
        avg_loss = pd.Series(loss).rolling(window=period).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI_OB'] = overbought
        df['RSI_OS'] = oversold
        return df

    @staticmethod
    def compute_signals(df, params):
        period = params['period']
        overbought = params['overbought']
        oversold = params['oversold']
        delta = df['close'].diff()
        gain = delta.clip(lower=0).rolling(window=period).mean()
        loss = -delta.clip(upper=0).rolling(window=period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI_LONG_SIGNAL'] = ((df['RSI'] < oversold) & (df['RSI'].shift(1) >= oversold)
                                 ).shift(1, fill_value=False).astype(int)
        df['RSI_SHORT_SIGNAL'] = ((df['RSI'] > overbought) & (df['RSI'].shift(1) <= overbought)
                                  ).shift(1, fill_value=False).astype(int)
