from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Bollinger(BaseIndicatorStrategy):
    """
    Bollinger Bands are a volatility-based technical indicator.
    They consist of a moving average (MA) and two bands above and below it,
    set at a certain number of standard deviations. Prices that break the bands
    may signal volatility and possible trend reversals.

    Hyperparameters:
        period: int
            The window size for the moving average and standard deviation (e.g., 10–40).
        stddev: float
            The number of standard deviations for the upper and lower bands (typically 1.5–3.5).

    Signal Logic:
        - Long signal: Price closes above the upper band (breakout).
        - Short signal: Price closes below the lower band (breakdown).
    """

    def __init__(self):
        super().__init__(IndicatorName.BOLLINGER.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–40 (inclusive), stddev: 1.5 to 3.5 in steps of 0.5
        period_range = list(range(10, 41))  # 10, 11, ..., 40
        stddev_range = [round(x, 2) for x in [1.5 + 0.5 * i for i in range(5)]]  # 1.5, 2.0, ..., 3.5
        return {
            "period": period_range,
            "stddev": stddev_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, stddev > 0
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['stddev'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'stddev' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'stddev' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        stddev = params['stddev']
        suffix = df_col_suffix or ""

        ma = df['close'].rolling(window=period, min_periods=period).mean()
        std = df['close'].rolling(window=period, min_periods=period).std()

        upper = ma + (stddev * std)
        lower = ma - (stddev * std)

        cross_up = (df['close'] > upper) & (df['close'].shift(1) <= upper.shift(1))
        cross_down = (df['close'] < lower) & (df['close'].shift(1) >= lower.shift(1))

        new_cols = {
            f'BOLLINGER_UPPER{suffix}': upper,
            f'BOLLINGER_LOWER{suffix}': lower,
            f'BOLLINGER_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'BOLLINGER_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int),
        }
        return new_cols
