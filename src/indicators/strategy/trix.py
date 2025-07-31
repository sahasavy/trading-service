from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class TRIX(BaseIndicatorStrategy):
    """
    The TRIX indicator is a momentum oscillator that shows the percent rate of change
    of a triple-smoothed EMA. It is used to identify oversold/overbought conditions,
    momentum, and trend direction.

    Hyperparameters:
        period: int
            The lookback period for the EMA calculations (typical: 10–30).

    Signal Logic:
        - Long signal: TRIX crosses above 0 (positive momentum).
        - Short signal: TRIX crosses below 0 (negative momentum).
    """

    def __init__(self):
        super().__init__(IndicatorName.TRIX.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–30 (inclusive)
        period_range = list(range(10, 31))  # 10, 11, ..., 30
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

        ema1 = df['close'].ewm(span=period, adjust=False, min_periods=period).mean()
        ema2 = ema1.ewm(span=period, adjust=False, min_periods=period).mean()
        ema3 = ema2.ewm(span=period, adjust=False, min_periods=period).mean()
        trix = ema3.pct_change() * 100

        new_cols = {
            f'TRIX{suffix}': trix,
            f'TRIX_LONG_SIGNAL{suffix}': (trix > 0).shift(1, fill_value=False).astype(int),
            f'TRIX_SHORT_SIGNAL{suffix}': (trix < 0).shift(1, fill_value=False).astype(int)
        }
        return new_cols
