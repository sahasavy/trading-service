from src.indicators.base import Indicator


class CCI(Indicator):
    def __init__(self):
        super().__init__("CCI")

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
