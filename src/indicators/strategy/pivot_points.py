from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Pivot(BaseIndicatorStrategy):
    """
    Pivot Points are commonly used support and resistance levels based on the previous bar's high, low, and close.
    They help traders identify possible turning points and trend direction for the current session.

    Hyperparameters:
        ma_period: int (optional)
            If set, a moving average of pivot points is used for signal smoothing (typical: 2–20).

    Signal Logic:
        - Long signal: Close crosses above the (MA of) pivot point.
        - Short signal: Close crosses below the (MA of) pivot point.
    """

    def __init__(self):
        super().__init__(IndicatorName.PIVOT.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Optional MA smoothing: 2–20 (default: just pivot)
        ma_period_range = [1] + list(range(2, 21))  # 1 means no smoothing, 2..20 = smoothed
        return {
            "ma_period": ma_period_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Only allow ma_period >= 1
        return [
            combo for combo in combos
            if combo['ma_period'] >= 1
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'ma_period' not in params:
            raise ValueError(
                f"{self.name} param 'ma_period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        ma_period = params['ma_period']
        suffix = df_col_suffix or ""

        pivot = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1)) / 3

        if ma_period > 1:
            pivot_ma = pivot.rolling(window=ma_period, min_periods=ma_period).mean()
            signal_series = pivot_ma
        else:
            signal_series = pivot

        new_cols = {
            f'PIVOT{suffix}': signal_series,
            f'PIVOT_LONG_SIGNAL{suffix}': (df['close'] > signal_series).shift(1, fill_value=False).astype(int),
            f'PIVOT_SHORT_SIGNAL{suffix}': (df['close'] < signal_series).shift(1, fill_value=False).astype(int)
        }
        return new_cols
