from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class SMACross(BaseIndicatorStrategy):
    """
    Simple Moving Average Crossover is a classic trend-following trading indicator.
    It generates buy and sell signals based on the crossover of two simple moving averages
    calculated over different window sizes.

    Hyperparameters:
        fast: int
            The lookback period for the "fast" SMA (typically short-term, e.g., 5-50).
        slow: int
            The lookback period for the "slow" SMA (typically longer-term, e.g., 20-200).

    Signal Logic:
        - Long signal: When the fast SMA crosses above the slow SMA (bullish crossover).
        - Short signal: When the fast SMA crosses below the slow SMA (bearish crossover).
    """

    def __init__(self):
        super().__init__(IndicatorName.SMA_CROSS.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # Domain range: Fast SMA 5–50, Slow SMA 20–200 (inclusive, integer step 1)
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
            if 0 < combo['fast'] < combo['slow'] != combo['fast'] and combo['slow'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'fast' not in params or 'slow' not in params:
            raise ValueError(
                f"{self.name} params 'fast' and 'slow' are required in backtest-config.yaml/indicator-config.yaml"
            )

        fast = params['fast']
        slow = params['slow']
        suffix = df_col_suffix or ""

        sma_fast = df['close'].rolling(window=fast, min_periods=fast).mean()
        sma_slow = df['close'].rolling(window=slow, min_periods=slow).mean()

        # Detect crossovers only, not just above/below
        cross_up = (sma_fast > sma_slow) & (sma_fast.shift(1) <= sma_slow.shift(1))
        cross_down = (sma_fast < sma_slow) & (sma_fast.shift(1) >= sma_slow.shift(1))

        new_cols = {
            f'SMA_FAST{suffix}': sma_fast,
            f'SMA_SLOW{suffix}': sma_slow,
            # Shift by 1 bar for lookahead safety
            f'SMA_CROSS_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'SMA_CROSS_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int),
        }
        return new_cols
