from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Envelope(BaseIndicatorStrategy):
    """
    The Envelope indicator consists of a moving average and two bands set at fixed percentage distances
    above and below the moving average. It is used to identify overbought or oversold conditions.

    Hyperparameters:
        period: int
            The lookback window for the moving average (typical: 10–40).
        percent: float
            The percentage distance for the upper and lower envelopes (typical: 0.01–0.05).

    Signal Logic:
        - Long signal: Price closes above the upper envelope (breakout).
        - Short signal: Price closes below the lower envelope (breakdown).
    """

    def __init__(self):
        super().__init__(IndicatorName.ENVELOPE.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–40 (inclusive), percent: 0.01, 0.02, ..., 0.05
        period_range = list(range(10, 41))  # 10, 11, ..., 40
        percent_range = [round(x, 3) for x in [0.01 * i for i in range(1, 6)]]  # 0.01, 0.02, ..., 0.05
        return {
            "period": period_range,
            "percent": percent_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, percent > 0
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['percent'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'percent' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'percent' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        percent = params['percent']
        suffix = df_col_suffix or ""

        ma = df['close'].rolling(window=period, min_periods=period).mean()
        upper = ma * (1 + percent)
        lower = ma * (1 - percent)
        cross_up = (df['close'] > upper)
        cross_down = (df['close'] < lower)

        new_cols = {
            f'ENVELOPE_UPPER{suffix}': upper,
            f'ENVELOPE_LOWER{suffix}': lower,
            f'ENVELOPE_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'ENVELOPE_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
