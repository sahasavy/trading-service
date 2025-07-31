from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class EMACross(BaseIndicatorStrategy):
    """
    The Exponential Moving Average (EMA) Crossover strategy is a trend-following approach
    that generates signals when a "fast" EMA crosses above or below a "slow" EMA.
    Crossovers are often used to identify shifts in momentum and trend direction.

    Hyperparameters:
        fast: int
            The span (lookback window) for the fast EMA (typical: 5–50).
        slow: int
            The span for the slow EMA (typical: 20–200).

    Signal Logic:
        - Long signal: Fast EMA crosses above Slow EMA (bullish crossover).
        - Short signal: Fast EMA crosses below Slow EMA (bearish crossover).
    """

    def __init__(self):
        super().__init__(IndicatorName.EMA_CROSS.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Domain knowledge: Fast EMA 5–50, Slow EMA 20–200 (inclusive, integer step 1)
        fast_range = list(range(5, 51))  # 5, 6, ..., 50
        slow_range = list(range(20, 201))  # 20, 21, ..., 200
        return {
            "fast": fast_range,
            "slow": slow_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # Only allow fast < slow and both > 0, not equal
        return [
            combo for combo in combos
            if
            0 < combo['fast'] < combo['slow'] != combo['fast'] and combo['slow'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        """
        Adds lookahead-safe EMA cross signals to df:
          - 'EMA_FAST'
          - 'EMA_SLOW'
          - 'EMA_CROSS_LONG_SIGNAL': 1 if previous bar fast crossed above slow (bullish), else 0
          - 'EMA_CROSS_SHORT_SIGNAL': 1 if previous bar fast crossed below slow (bearish), else 0
        """
        if 'fast' not in params or 'slow' not in params:
            raise ValueError(
                f"{self.name} params 'fast' and 'slow' are required in backtest-config.yaml/indicator-config.yaml"
            )

        fast = params['fast']
        slow = params['slow']
        suffix = df_col_suffix or ""

        ema_fast = df['close'].ewm(span=fast, adjust=False, min_periods=fast).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False, min_periods=slow).mean()

        # Detect crossovers only, not just above/below
        cross_up = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
        cross_down = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

        new_cols = {
            f'EMA_FAST{suffix}': ema_fast,
            f'EMA_SLOW{suffix}': ema_slow,
            # Shift by 1 bar for lookahead safety
            f'EMA_CROSS_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'EMA_CROSS_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
