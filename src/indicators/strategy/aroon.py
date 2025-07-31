import numpy as np
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Aroon(BaseIndicatorStrategy):
    """
    The Aroon indicator is a trend-following indicator used to identify whether a stock is in a trend,
    and how strong that trend is. It consists of two lines: Aroon Up and Aroon Down.
    The indicator calculates how many periods have passed since the highest high (Aroon Up) or
    the lowest low (Aroon Down) within a given period. Both are scaled 0–100.

    Hyperparameters:
        period: int
            The lookback period to check for highs/lows (typical: 10–50).

    Signal Logic:
        - Long signal: Aroon Up crosses above 70 (strong uptrend).
        - Short signal: Aroon Down crosses above 70 (strong downtrend).
    """

    def __init__(self):
        super().__init__(IndicatorName.AROON.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Realistic period range for Aroon is 10–50
        period_range = list(range(10, 51))  # 10, 11, ..., 50
        return {
            "period": period_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Only allow period > 1
        return [
            combo for combo in combos
            if combo['period'] > 1
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params:
            raise ValueError(
                f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        suffix = df_col_suffix or ""

        # Aroon Up: % of time since highest high in last 'period' bars
        aroon_up = df['high'].rolling(window=period + 1).apply(
            lambda x: float(np.argmax(x[::-1])) / period * 100, raw=True
        )
        # Aroon Down: % of time since lowest low in last 'period' bars
        aroon_down = df['low'].rolling(window=period + 1).apply(
            lambda x: float(np.argmin(x[::-1])) / period * 100, raw=True
        )

        new_cols = {
            f'AROON_UP{suffix}': aroon_up,
            f'AROON_DOWN{suffix}': aroon_down,
            f'AROON_LONG_SIGNAL{suffix}': (aroon_up > 70).shift(1, fill_value=False).astype(int),
            f'AROON_SHORT_SIGNAL{suffix}': (aroon_down > 70).shift(1, fill_value=False).astype(int),
        }
        return new_cols
