import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class UltimateOsc(BaseIndicatorStrategy):
    """
    The Ultimate Oscillator is a momentum oscillator that combines short, intermediate,
    and long-term price action into a single value. It is less prone to false signals
    and is commonly used to spot divergences and overbought/oversold levels.

    Hyperparameters:
        period_short: int
            Short-term lookback (classic: 7)
        period_medium: int
            Medium-term lookback (classic: 14)
        period_long: int
            Long-term lookback (classic: 28)

    Signal Logic:
        - Long signal: Ultimate Oscillator > 70 (overbought).
        - Short signal: Ultimate Oscillator < 30 (oversold).
    """

    def __init__(self):
        super().__init__(IndicatorName.ULTIMATE_OSC.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Allow classic and common ranges for all three periods
        period_short_range = list(range(5, 11))  # 5,6,...10
        period_medium_range = list(range(10, 21))  # 10,11,...20
        period_long_range = list(range(21, 31))  # 21,22,...30
        return {
            "period_short": period_short_range,
            "period_medium": period_medium_range,
            "period_long": period_long_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period_short < period_medium < period_long, all > 1
        return [
            combo for combo in combos
            if 1 < combo['period_short'] < combo['period_medium'] < combo['period_long']
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        for key in ['period_short', 'period_medium', 'period_long']:
            if key not in params:
                raise ValueError(
                    f"{self.name} param '{key}' is required in backtest-config.yaml/indicator-config.yaml"
                )

        period_short = params['period_short']
        period_medium = params['period_medium']
        period_long = params['period_long']
        suffix = df_col_suffix or ""

        high, low, close = df['high'], df['low'], df['close']
        prev_close = close.shift(1)

        bp = close - pd.concat([low, prev_close], axis=1).min(axis=1)
        tr = (pd.concat([high, prev_close], axis=1).max(axis=1) -
              pd.concat([low, prev_close], axis=1).min(axis=1))

        avg_short = (bp.rolling(period_short, min_periods=period_short).sum() /
                     tr.rolling(period_short, min_periods=period_short).sum())
        avg_medium = (bp.rolling(period_medium, min_periods=period_medium).sum() /
                      tr.rolling(period_medium, min_periods=period_medium).sum())
        avg_long = (bp.rolling(period_long, min_periods=period_long).sum() /
                    tr.rolling(period_long, min_periods=period_long).sum())

        uo = 100 * ((4 * avg_short) + (2 * avg_medium) + avg_long) / 7

        new_cols = {
            f'ULTIMATE_OSC{suffix}': uo,
            f'ULTIMATE_OSC_LONG_SIGNAL{suffix}': (uo > 70).shift(1, fill_value=False).astype(int),
            f'ULTIMATE_OSC_SHORT_SIGNAL{suffix}': (uo < 30).shift(1, fill_value=False).astype(int)
        }
        return new_cols
