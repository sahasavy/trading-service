from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Donchian(BaseIndicatorStrategy):
    """
    The Donchian Channel plots the highest high and lowest low over a specified period.
    It is often used to identify breakouts and trend-following opportunities.

    Hyperparameters:
        period: int
            The lookback window to compute the upper and lower channels (typical: 10–40).

    Signal Logic:
        - Long signal: Price closes above the previous bar's channel high (breakout).
        - Short signal: Price closes below the previous bar's channel low (breakdown).
    """

    def __init__(self):
        super().__init__(IndicatorName.DONCHIAN.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Donchian period: 10–40 (inclusive)
        period_range = list(range(10, 41))  # 10, 11, ..., 40
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
            raise ValueError(f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml")

        period = params['period']
        suffix = df_col_suffix or ""

        dc_high = df['high'].rolling(window=period, min_periods=period).max()
        dc_low = df['low'].rolling(window=period, min_periods=period).min()

        cross_up = (df['close'] > dc_high.shift(1))
        cross_down = (df['close'] < dc_low.shift(1))

        new_cols = {
            f'DONCHIAN_HIGH{suffix}': dc_high,
            f'DONCHIAN_LOW{suffix}': dc_low,
            f'DONCHIAN_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'DONCHIAN_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int),
        }
        return new_cols
