from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class WilliamsR(BaseIndicatorStrategy):
    """
    Williams %R is a momentum oscillator measuring overbought and oversold levels,
    scaled from -100 (most oversold) to 0 (most overbought).

    Hyperparameters:
        period: int
            Lookback window for high/low (typical: 7–30).
        overbought: int
            Threshold above which an instrument is considered overbought (e.g., -10 to -20).
        oversold: int
            Threshold below which an instrument is considered oversold (e.g., -70 to -90).

    Signal Logic:
        - Long signal: Williams %R falls below oversold threshold.
        - Short signal: Williams %R rises above overbought threshold.
    """

    def __init__(self):
        super().__init__(IndicatorName.WILLIAMS_R.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 7–30, overbought: -10 to -30 (step -5), oversold: -70 to -90 (step -5)
        period_range = list(range(7, 31))  # 7, 8, ..., 30
        overbought_range = list(range(-10, -31, -5))  # -10, -15, -20, -25, -30
        oversold_range = list(range(-70, -91, -5))  # -70, -75, -80, -85, -90
        return {
            "period": period_range,
            "overbought": overbought_range,
            "oversold": oversold_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, overbought > oversold (e.g. -20 > -80 numerically)
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['overbought'] > combo['oversold']
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'overbought' not in params or 'oversold' not in params:
            raise ValueError(
                f"{self.name} params 'period', 'overbought', and 'oversold' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        overbought = params['overbought']
        oversold = params['oversold']
        suffix = df_col_suffix or ""

        high_roll = df['high'].rolling(window=period, min_periods=period).max()
        low_roll = df['low'].rolling(window=period, min_periods=period).min()
        denominator = (high_roll - low_roll).replace(0, 1e-9)  # avoid division by zero
        wr = -100 * ((high_roll - df['close']) / denominator)

        new_cols = {
            f'WILLIAMSR{suffix}': wr,
            f'WILLIAMS_R_LONG_SIGNAL{suffix}': (wr < oversold).shift(1, fill_value=False).astype(int),
            f'WILLIAMS_R_SHORT_SIGNAL{suffix}': (wr > overbought).shift(1, fill_value=False).astype(int)
        }
        return new_cols
