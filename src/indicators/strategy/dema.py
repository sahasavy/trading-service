from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class DEMA(BaseIndicatorStrategy):
    """
    The Double Exponential Moving Average (DEMA) reduces lag compared to a standard EMA
    by combining an EMA and a second EMA of the first EMA. It is useful for trend following.

    Hyperparameters:
        period: int
            The lookback period for the EMA calculations (typical: 10–40).

    Signal Logic:
        - Long signal: Price closes above DEMA (bullish momentum).
        - Short signal: Price closes below DEMA (bearish momentum).
    """

    def __init__(self):
        super().__init__(IndicatorName.DEMA.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # DEMA period: 10–40 (inclusive)
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
            raise ValueError(
                f"{self.name} param 'period' is required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        suffix = df_col_suffix or ""

        ema1 = df['close'].ewm(span=period, adjust=False, min_periods=period).mean()
        ema2 = ema1.ewm(span=period, adjust=False, min_periods=period).mean()
        dema = 2 * ema1 - ema2

        cross_up = (df['close'] > dema) & (df['close'].shift(1) <= dema.shift(1))
        cross_down = (df['close'] < dema) & (df['close'].shift(1) >= dema.shift(1))

        new_cols = {
            f'DEMA{suffix}': dema,
            f'DEMA_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'DEMA_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
