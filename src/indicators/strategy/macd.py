from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class MACD(BaseIndicatorStrategy):
    """
    MACD is a momentum-following trend indicator that shows the relationship between two EMAs of closing price.
    It consists of the MACD line (difference between fast and slow EMA), a signal line (EMA of MACD), and
    is often used to identify bullish or bearish crossovers.

    Hyperparameters:
        fast: int
            Span for the fast EMA (typical: 8–20).
        slow: int
            Span for the slow EMA (typical: 20–40).
        signal: int
            Span for the signal EMA of the MACD line (typical: 7–15).

    Signal Logic:
        - Long signal: MACD crosses above Signal line.
        - Short signal: MACD crosses below Signal line.
    """

    def __init__(self):
        super().__init__(IndicatorName.MACD.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # fast: 8–20, slow: 20–40, signal: 7–15
        fast_range = list(range(8, 21))  # 8, 9, ..., 20
        slow_range = list(range(20, 41))  # 20, 21, ..., 40
        signal_range = list(range(7, 16))  # 7, 8, ..., 15
        return {
            "fast": fast_range,
            "slow": slow_range,
            "signal": signal_range,
        }

    @classmethod
    def filter_valid_grid_combos(cls, combos):
        # fast < slow, all > 0, not equal
        return [
            combo for combo in combos
            if 0 < combo['fast'] < combo['slow'] != combo['fast']
               and combo['slow'] > 0
               and combo['signal'] > 0
        ]

    def compute_signals(self, df, params, df_col_suffix=None):
        if 'fast' not in params or 'slow' not in params or 'signal' not in params:
            raise ValueError(
                f"{self.name} params 'fast', 'slow', and 'signal' are required in backtest-config.yaml/indicator-config.yaml"
            )

        fast = params['fast']
        slow = params['slow']
        signal = params['signal']
        suffix = df_col_suffix or ""

        ema_fast = df['close'].ewm(span=fast, adjust=False, min_periods=fast).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False, min_periods=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False, min_periods=signal).mean()

        cross_up = (macd > macd_signal) & (macd.shift(1) <= macd_signal.shift(1))
        cross_down = (macd < macd_signal) & (macd.shift(1) >= macd_signal.shift(1))

        new_cols = {
            f'EMA_FAST{suffix}': ema_fast,
            f'EMA_SLOW{suffix}': ema_slow,
            f'MACD{suffix}': macd,
            f'MACD_SIGNAL{suffix}': macd_signal,
            f'MACD_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'MACD_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
