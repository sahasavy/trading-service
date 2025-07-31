from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Momentum(BaseIndicatorStrategy):
    """
    The Momentum indicator measures the rate of change of closing prices.
    It is used to identify the speed and direction of price movement.

    Hyperparameters:
        period: int
            The difference window for calculating momentum (typical: 5–30).

    Signal Logic:
        - Long signal: Momentum rises above zero.
        - Short signal: Momentum falls below zero.
    """

    def __init__(self):
        super().__init__(IndicatorName.MOMENTUM.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 5–30 (inclusive)
        period_range = list(range(5, 31))  # 5, 6, ..., 30
        return {
            "period": period_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Only allow period > 0
        return [
            combo for combo in combos
            if combo['period'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params:
            raise ValueError(
                f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        suffix = df_col_suffix or ""

        momentum = df['close'].diff(period)

        new_cols = {
            f'MOMENTUM{suffix}': momentum,
            f'MOMENTUM_LONG_SIGNAL{suffix}': (momentum > 0).shift(1, fill_value=False).astype(int),
            f'MOMENTUM_SHORT_SIGNAL{suffix}': (momentum < 0).shift(1, fill_value=False).astype(int)
        }
        return new_cols
