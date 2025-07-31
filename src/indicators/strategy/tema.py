from src.commons.constants.constants import IndicatorName
from src.indicators.base_indicator_strategy import BaseIndicatorStrategy


class TEMA(BaseIndicatorStrategy):
    """
    The Triple Exponential Moving Average (TEMA) reduces lag and increases responsiveness
    compared to single or double EMA. TEMA is often used as a trend-following indicator.

    Hyperparameters:
        period: int
            The lookback period for all EMA calculations (typical: 10–40).

    Signal Logic:
        - Long signal: Price closes above TEMA (momentum up).
        - Short signal: Price closes below TEMA (momentum down).
    """

    def __init__(self):
        super().__init__(IndicatorName.TEMA.name)

    @classmethod
    def grid_ranges(cls, default_params):
        # period: 10–40 (inclusive)
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
        ema3 = ema2.ewm(span=period, adjust=False, min_periods=period).mean()
        tema = 3 * (ema1 - ema2) + ema3

        cross_up = (df['close'] > tema) & (df['close'].shift(1) <= tema.shift(1))
        cross_down = (df['close'] < tema) & (df['close'].shift(1) >= tema.shift(1))

        new_cols = {
            f'TEMA{suffix}': tema,
            f'TEMA_LONG_SIGNAL{suffix}': cross_up.shift(1, fill_value=False).astype(int),
            f'TEMA_SHORT_SIGNAL{suffix}': cross_down.shift(1, fill_value=False).astype(int)
        }
        return new_cols
