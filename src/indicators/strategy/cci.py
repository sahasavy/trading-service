import numpy as np

from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class CCI(BaseIndicatorStrategy):
    """
    IndicatorStrategy --> Commodity Channel Index (CCI)
    """

    def __init__(self):
        super().__init__(IndicatorName.CCI.name)

    def calculate(self, df, **params):
        if 'period' not in params or 'entry' not in params or 'exit' not in params:
            raise ValueError("CCI params 'period', 'entry', and 'exit' are required in indicator-config.yaml")
        period = params['period']
        entry_val = params['entry']
        exit_val = params['exit']
        df = df.copy()
        tp = (df['high'] + df['low'] + df['close']) / 3
        tp_sma = tp.rolling(window=period).mean()
        mean_dev = (tp - tp_sma).abs().rolling(window=period).mean()
        cci = (tp - tp_sma) / (0.015 * mean_dev + 1e-9)
        df['CCI'] = cci
        df['CCI_ENTRY'] = entry_val
        df['CCI_EXIT'] = exit_val
        return df

    @staticmethod
    def compute_signals(df, params):
        period = params.get('period', 20)
        entry_val = params.get('entry', -100)
        exit_val = params.get('exit', 100)
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period).mean()
        md = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        cci = (tp - ma) / (0.015 * md)
        df['CCI'] = cci
        df['CCI_LONG_SIGNAL'] = (cci < entry_val).shift(1, fill_value=False).astype(int)
        df['CCI_SHORT_SIGNAL'] = (cci > exit_val).shift(1, fill_value=False).astype(int)
