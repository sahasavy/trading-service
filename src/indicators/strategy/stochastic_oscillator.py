from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Stochastic(BaseIndicatorStrategy):
    """
    The Stochastic Oscillator is a momentum indicator comparing a particular closing price
    to a range of prices over a certain period. It is used to identify overbought and oversold levels.

    Hyperparameters:
        k_period: int
            The lookback period for %K line (typical: 7–21).
        d_period: int
            The smoothing period for %D line (typical: 2–7).
        overbought: int or float
            The upper threshold above which an instrument is considered overbought (typical: 70–90).
        oversold: int or float
            The lower threshold below which an instrument is considered oversold (typical: 10–30).

    Signal Logic:
        - Long signal: %K falls below oversold threshold.
        - Short signal: %K rises above overbought threshold.
    """

    def __init__(self):
        super().__init__(IndicatorName.STOCHASTIC.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # k_period: 7–21, d_period: 2–7, overbought: 70–90, oversold: 10–30
        k_period_range = list(range(7, 22))  # 7, 8, ..., 21
        d_period_range = list(range(2, 8))  # 2, 3, ..., 7
        overbought_range = list(range(70, 91, 5))  # 70, 75, ..., 90
        oversold_range = list(range(10, 31, 5))  # 10, 15, ..., 30
        return {
            "k_period": k_period_range,
            "d_period": d_period_range,
            "overbought": overbought_range,
            "oversold": oversold_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # k_period > 1, d_period > 0, overbought > oversold
        return [
            combo for combo in combos
            if combo['k_period'] > 1 and combo['d_period'] > 0 and combo['overbought'] > combo['oversold']
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'k_period' not in params or 'd_period' not in params or 'overbought' not in params or 'oversold' not in params:
            raise ValueError(
                f"{self.name} params 'k_period', 'd_period', 'overbought', and 'oversold' are required in backtest-config.yaml/indicator-config.yaml"
            )

        k_period = params['k_period']
        d_period = params['d_period']
        overbought = params['overbought']
        oversold = params['oversold']
        suffix = df_col_suffix or ""

        high_roll = df['high'].rolling(window=k_period, min_periods=k_period).max()
        low_roll = df['low'].rolling(window=k_period, min_periods=k_period).min()
        denominator = (high_roll - low_roll).replace(0, 1e-9)  # Avoid division by zero

        k = 100 * ((df['close'] - low_roll) / denominator)
        d = k.rolling(window=d_period, min_periods=d_period).mean()

        new_cols = {
            f'STOCH_K{suffix}': k,
            f'STOCH_D{suffix}': d,
            f'STOCHASTIC_LONG_SIGNAL{suffix}': (k < oversold).shift(1, fill_value=False).astype(int),
            f'STOCHASTIC_SHORT_SIGNAL{suffix}': (k > overbought).shift(1, fill_value=False).astype(int),
        }
        return new_cols
