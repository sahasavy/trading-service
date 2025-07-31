import pandas as pd
from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class ADX(BaseIndicatorStrategy):
    """
    The Average Directional Index (ADX) is a momentum indicator used to quantify trend strength.
    It is derived from two other indicators: the Positive Directional Indicator (+DI) and the Negative Directional Indicator (−DI).
    ADX values above a threshold (e.g., 25) are typically interpreted as strong trends.

    Hyperparameters:
        period: int
            The number of bars over which to compute the indicators (typical range: 7–30).
        threshold: int or float
            The ADX value above which a trend is considered strong (e.g., 20–40).
        exit_threshold: int or float
            The ADX value below which a trend is considered weak and a position may be exited (e.g., 10–30).

    Signal Logic:
        - Long signal: ADX > threshold AND +DI > −DI (strong uptrend)
        - Short signal: ADX > threshold AND −DI > +DI (strong downtrend)
    """

    def __init__(self):
        super().__init__(IndicatorName.ADX.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Typical ranges: period 7–30, threshold 20–40, exit_threshold 10–30 (all ints for simplicity)
        period_range = list(range(7, 31))  # 7, 8, ..., 30
        threshold_range = list(range(20, 41))  # 20, 21, ..., 40
        exit_threshold_range = list(range(10, 31))  # 10, 11, ..., 30
        return {
            "period": period_range,
            "threshold": threshold_range,
            "exit_threshold": exit_threshold_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Valid: period > 1, threshold >= exit_threshold, all positive
        return [
            combo for combo in combos
            if combo['period'] > 1
               and combo['threshold'] >= combo['exit_threshold']
               and combo['threshold'] > 0
               and combo['exit_threshold'] >= 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'threshold' not in params or 'exit_threshold' not in params:
            raise ValueError(
                f"{self.name} params 'period', 'threshold', and 'exit_threshold' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        threshold = params['threshold']
        exit_threshold = params['exit_threshold']
        suffix = df_col_suffix or ""

        high = df['high']
        low = df['low']
        close = df['close']

        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period, min_periods=period).mean()

        plus_di = 100 * (plus_dm.rolling(period, min_periods=period).sum() / atr)
        minus_di = 100 * (abs(minus_dm.rolling(period, min_periods=period).sum()) / atr)
        dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
        adx = dx.rolling(period, min_periods=period).mean()

        new_cols = {
            f'ADX{suffix}': adx,
            f'ADX_LONG_SIGNAL{suffix}': ((adx > threshold) & (plus_di > minus_di)
                                         ).shift(1, fill_value=False).astype(int),
            f'ADX_SHORT_SIGNAL{suffix}': ((adx > threshold) & (minus_di > plus_di)
                                          ).shift(1, fill_value=False).astype(int),
            f'ADX_LONG_EXIT_SIGNAL{suffix}': ((adx < exit_threshold) & (plus_di > minus_di)
                                              ).shift(1, fill_value=False).astype(int),
            f'ADX_SHORT_EXIT_SIGNAL{suffix}': ((adx < exit_threshold) & (minus_di > plus_di)
                                               ).shift(1, fill_value=False).astype(int),
        }
        return new_cols
