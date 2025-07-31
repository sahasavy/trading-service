from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class Keltner(BaseIndicatorStrategy):
    """
    The Keltner Channel is a volatility-based envelope set above and below an exponential moving average (EMA).
    The bands are set a multiple of the Average True Range (ATR) or (in this simple version) the range of high-low.

    Hyperparameters:
        period: int
            The lookback window for EMA and ATR calculation (typical: 10–40).
        multiplier: float
            The multiple of ATR/range to set the channel width (typical: 1.5–3.5).

    Signal Logic:
        - Long signal: Price closes above the upper channel.
        - Short signal: Price closes below the lower channel.
    """

    def __init__(self):
        super().__init__(IndicatorName.KELTNER.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–40, multiplier: 1.5–3.5 by 0.5 steps
        period_range = list(range(10, 41))
        multiplier_range = [round(1.5 + 0.5 * i, 2) for i in range(5)]  # 1.5, 2.0, ..., 3.5
        return {
            "period": period_range,
            "multiplier": multiplier_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # period > 1, multiplier > 0
        return [
            combo for combo in combos
            if combo['period'] > 1 and combo['multiplier'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'period' not in params or 'multiplier' not in params:
            raise ValueError(
                f"{self.name} params 'period' and 'multiplier' are required in backtest-config.yaml/indicator-config.yaml"
            )

        period = params['period']
        atr_mult = params['multiplier']
        suffix = df_col_suffix or ""

        ema = df['close'].ewm(span=period, adjust=False, min_periods=period).mean()
        atr = (df['high'] - df['low']).rolling(window=period, min_periods=period).mean()
        upper = ema + atr_mult * atr
        lower = ema - atr_mult * atr

        cross_up = (df['close'] > upper)
        cross_down = (df['close'] < lower)

        new_cols = {
            f'KELTNER_UPPER{suffix}': upper,
            f'KELTNER_LOWER{suffix}': lower,
            f'KELTNER_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'KELTNER_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
