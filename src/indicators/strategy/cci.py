import numpy as np
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class CCI(BaseIndicatorStrategy):
    """
    The Commodity Channel Index (CCI) is a versatile momentum-based oscillator
    that measures the deviation of price from its statistical mean. CCI is
    commonly used to identify cyclical trends in an instrument.

    Hyperparameters:
        period: int
            The lookback window for typical price averaging (typical: 10–40).
        entry: int or float
            The CCI threshold below which a long signal is considered (e.g., -100).
        exit: int or float
            The CCI threshold above which a short signal is considered (e.g., +100).

    Signal Logic:
        - Long signal: CCI crosses below the entry threshold (oversold).
        - Short signal: CCI crosses above the exit threshold (overbought).
    """

    def __init__(self):
        super().__init__(IndicatorName.CCI.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–40 (inclusive)
        # entry: -200 to -50 (step 25), exit: 50 to 200 (step 25)
        period_range = list(range(10, 41))  # 10, 11, ..., 40
        entry_range = list(range(-200, -49, 25))  # -200, -175, ..., -50
        exit_range = list(range(50, 201, 25))  # 50, 75, ..., 200
        return {
            "period": period_range,
            "entry": entry_range,
            "exit": exit_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, entry < exit
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['entry'] < combo['exit']
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'entry' not in params or 'exit' not in params:
            raise ValueError(
                f"{self.name} params 'period', 'entry', and 'exit' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        entry_val = params['entry']
        exit_val = params['exit']
        suffix = df_col_suffix or ""

        tp = (df['high'] + df['low'] + df['close']) / 3
        ma = tp.rolling(period, min_periods=period).mean()
        md = tp.rolling(period, min_periods=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        cci = (tp - ma) / (0.015 * md)

        new_cols = {
            f'CCI{suffix}': cci,
            f'CCI_LONG_SIGNAL{suffix}': (cci < entry_val).shift(1, fill_value=False).astype(int),
            f'CCI_SHORT_SIGNAL{suffix}': (cci > exit_val).shift(1, fill_value=False).astype(int),
        }
        return new_cols
